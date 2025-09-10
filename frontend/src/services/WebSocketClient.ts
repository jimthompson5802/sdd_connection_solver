/**
 * WebSocket client service for real-time communication with the backend
 */
export interface WebSocketMessage {
  type: string;
  data: unknown;
}

export interface RecommendationUpdate {
  sessionId: string;
  recommendationId: string;
  status: 'generating' | 'completed' | 'error';
  recommendation?: {
    id: string;
    words: string[];
    category: string;
    confidence: number;
    reasoning: string;
  };
  error?: string;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000;
  private eventHandlers: Map<string, Array<(data: unknown) => void>> = new Map();

  constructor(private url: string) {}

  /**
   * Connect to the WebSocket server
   */
  public connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Disconnect from the WebSocket server
   */
  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Send a message to the server
   */
  public send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected. Message not sent:', message);
    }
  }

  /**
   * Subscribe to specific message types
   */
  public on(messageType: string, handler: (data: unknown) => void): void {
    if (!this.eventHandlers.has(messageType)) {
      this.eventHandlers.set(messageType, []);
    }
    this.eventHandlers.get(messageType)!.push(handler);
  }

  /**
   * Unsubscribe from message types
   */
  public off(messageType: string, handler?: (data: unknown) => void): void {
    if (!this.eventHandlers.has(messageType)) {
      return;
    }

    if (handler) {
      const handlers = this.eventHandlers.get(messageType)!;
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    } else {
      this.eventHandlers.delete(messageType);
    }
  }

  /**
   * Subscribe to recommendation updates
   */
  public onRecommendationUpdate(handler: (update: RecommendationUpdate) => void): void {
    this.on('recommendation_update', handler as (data: unknown) => void);
  }

  /**
   * Subscribe to session state updates
   */
  public onSessionUpdate(handler: (data: unknown) => void): void {
    this.on('session_update', handler);
  }

  /**
   * Get the current connection state
   */
  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.eventHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => handler(message.data));
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect().catch(error => {
          console.error('Reconnection failed:', error);
        });
      }, this.reconnectInterval * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }
}

// Singleton instance for the application
export const wsClient = new WebSocketClient('ws://localhost:8000/ws');
