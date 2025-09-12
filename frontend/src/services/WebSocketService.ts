/**
 * WebSocket service for real-time updates in NYT Connections Puzzle Assistant
 * 
 * This service provides a high-level interface for WebSocket communication
 * specifically designed for the puzzle-solving workflow, including:
 * - Real-time recommendation delivery
 * - Session state updates
 * - Connection management with automatic reconnection
 * - Message queuing for offline scenarios
 */

export interface SessionState {
  sessionId: string;
  status: 'active' | 'completed' | 'failed' | 'abandoned';
  solvedGroupsCount: number;
  remainingWords: string[];
  incorrectEvaluationCount: number;
  pendingRecommendationId?: string;
}

export interface Recommendation {
  id: string;
  sessionId: string;
  recommendedWords: string[];
  explanation: string;
  processingTimeMs: number;
  llmModel: string;
  timestamp: string;
}

export interface RecommendationEvaluation {
  id: string;
  userEvaluation: 'correct' | 'incorrect' | 'one_away';
  evaluationTimestamp?: string;
}

export interface WebSocketServiceConfig {
  reconnectDelay: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
}

export type WebSocketEventHandler<T = any> = (data: T) => void;

export class WebSocketService {
  private websocket: WebSocket | null = null;
  private sessionId: string | null = null;
  private reconnectAttempts = 0;
  private isConnecting = false;
  private messageQueue: string[] = [];
  private heartbeatInterval: number | null = null;
  
  private readonly config: WebSocketServiceConfig = {
    reconnectDelay: 1000,
    maxReconnectAttempts: 5,
    heartbeatInterval: 30000
  };

  // Event handlers
  private eventHandlers: Map<string, WebSocketEventHandler[]> = new Map();

  constructor(private baseUrl: string = 'ws://localhost:8000', config?: Partial<WebSocketServiceConfig>) {
    if (config) {
      this.config = { ...this.config, ...config };
    }
  }

  /**
   * Connect to WebSocket for a specific session
   */
  public async connect(sessionId: string): Promise<void> {
    if (this.isConnecting) {
      throw new Error('Connection already in progress');
    }

    if (this.websocket?.readyState === WebSocket.OPEN && this.sessionId === sessionId) {
      console.log('WebSocket already connected to session:', sessionId);
      return;
    }

    this.sessionId = sessionId;
    this.isConnecting = true;

    try {
      await this.establishConnection(sessionId);
      this.startHeartbeat();
      this.processMessageQueue();
    } finally {
      this.isConnecting = false;
    }
  }

  /**
   * Disconnect from WebSocket
   */
  public disconnect(): void {
    this.stopHeartbeat();
    
    if (this.websocket) {
      this.websocket.close(1000, 'Client disconnecting');
      this.websocket = null;
    }

    this.sessionId = null;
    this.reconnectAttempts = 0;
    this.isConnecting = false;
    this.messageQueue = [];
  }

  /**
   * Check if WebSocket is connected
   */
  public get isConnected(): boolean {
    return this.websocket?.readyState === WebSocket.OPEN;
  }

  /**
   * Get current session ID
   */
  public get currentSessionId(): string | null {
    return this.sessionId;
  }

  /**
   * Request a new AI recommendation
   */
  public requestRecommendation(): void {
    this.sendMessage({
      type: 'request_recommendation'
    });
  }

  /**
   * Subscribe to session state updates
   */
  public onSessionUpdate(handler: WebSocketEventHandler<SessionState>): void {
    this.addEventListener('session_state', handler);
    this.addEventListener('session_updated', handler);
  }

  /**
   * Subscribe to new recommendations
   */
  public onNewRecommendation(handler: WebSocketEventHandler<Recommendation>): void {
    this.addEventListener('new_recommendation', handler);
  }

  /**
   * Subscribe to recommendation updates (evaluations)
   */
  public onRecommendationUpdate(handler: WebSocketEventHandler<RecommendationEvaluation>): void {
    this.addEventListener('recommendation_updated', handler);
  }

  /**
   * Subscribe to recommendation request acknowledgments
   */
  public onRecommendationRequestReceived(handler: WebSocketEventHandler<{ timestamp: string }>): void {
    this.addEventListener('recommendation_request_received', handler);
  }

  /**
   * Subscribe to connection status changes
   */
  public onConnectionChange(handler: WebSocketEventHandler<{ connected: boolean; sessionId?: string }>): void {
    this.addEventListener('connection_change', handler);
  }

  /**
   * Subscribe to error messages
   */
  public onError(handler: WebSocketEventHandler<{ error: string; timestamp: string }>): void {
    this.addEventListener('error', handler);
  }

  /**
   * Remove event listener
   */
  public removeEventListener(eventType: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Clear all event listeners
   */
  public clearEventListeners(): void {
    this.eventHandlers.clear();
  }

  private async establishConnection(sessionId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${this.baseUrl}/ws/sessions/${sessionId}/recommendations`;
      console.log('Connecting to WebSocket:', wsUrl);

      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log('WebSocket connected to session:', sessionId);
        this.reconnectAttempts = 0;
        this.emitEvent('connection_change', { connected: true, sessionId });
        resolve();
      };

      this.websocket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          this.emitEvent('error', { error: 'Failed to parse message', timestamp: new Date().toISOString() });
        }
      };

      this.websocket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.emitEvent('connection_change', { connected: false });
        this.websocket = null;

        // Attempt reconnection if not intentionally closed
        if (event.code !== 1000 && this.sessionId) {
          this.attemptReconnection();
        }
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket connection error:', error);
        this.emitEvent('error', { error: 'Connection failed', timestamp: new Date().toISOString() });
        reject(new Error('WebSocket connection failed'));
      };

      // Set connection timeout
      setTimeout(() => {
        if (this.websocket?.readyState !== WebSocket.OPEN) {
          this.websocket?.close();
          reject(new Error('WebSocket connection timeout'));
        }
      }, 10000);
    });
  }

  private handleMessage(message: any): void {
    console.log('Received WebSocket message:', message);

    switch (message.type) {
      case 'session_state':
      case 'session_updated':
        this.emitEvent(message.type, message.data);
        break;
      
      case 'new_recommendation':
        this.emitEvent('new_recommendation', message.data);
        break;
      
      case 'recommendation_updated':
        this.emitEvent('recommendation_updated', message.data);
        break;
      
      case 'recommendation_request_received':
        this.emitEvent('recommendation_request_received', { timestamp: message.timestamp });
        break;
      
      case 'error':
        this.emitEvent('error', { error: message.error, timestamp: message.timestamp });
        break;
      
      case 'pong':
        // Heartbeat response - connection is alive
        break;
      
      default:
        console.warn('Unknown message type:', message.type);
        break;
    }
  }

  private sendMessage(message: any): void {
    const messageString = JSON.stringify(message);

    if (this.isConnected) {
      this.websocket!.send(messageString);
    } else {
      console.warn('WebSocket not connected, queuing message:', message);
      this.messageQueue.push(messageString);
    }
  }

  private processMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.isConnected) {
      const message = this.messageQueue.shift()!;
      this.websocket!.send(message);
    }
  }

  private attemptReconnection(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emitEvent('error', { 
        error: 'Max reconnection attempts reached', 
        timestamp: new Date().toISOString() 
      });
      return;
    }

    this.reconnectAttempts++;
    const delay = this.config.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Attempting reconnection ${this.reconnectAttempts}/${this.config.maxReconnectAttempts} in ${delay}ms`);

    setTimeout(async () => {
      if (this.sessionId && !this.isConnected) {
        try {
          await this.establishConnection(this.sessionId);
          this.startHeartbeat();
          this.processMessageQueue();
        } catch (error) {
          console.error('Reconnection failed:', error);
          this.attemptReconnection();
        }
      }
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();

    this.heartbeatInterval = window.setInterval(() => {
      if (this.isConnected) {
        this.sendMessage({ type: 'ping' });
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private addEventListener(eventType: string, handler: WebSocketEventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }

  private emitEvent(eventType: string, data: any): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${eventType}:`, error);
        }
      });
    }
  }
}

// Export singleton instance for use across the application
export const webSocketService = new WebSocketService();

// Export for testing with custom configuration
export default WebSocketService;
