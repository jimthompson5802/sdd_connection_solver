/**
 * Main application component connecting all features for NYT Connections Puzzle Assistant.
 * 
 * This component orchestrates the entire frontend application, managing:
 * - Application state and navigation
 * - Component lifecycle and coordination
 * - Service integration (API, WebSocket, Game State)
 * - Event handling and error management
 */

import { WebSocketService, webSocketService } from './services/WebSocketService';
import { GameStateManager } from './services/GameState';
import { ApiService } from './services/ApiService';

// Component imports (these will be created in subsequent tasks)
import { FileUpload } from './components/FileUpload';
import { PuzzleView } from './components/PuzzleView';
import { RecommendationCard } from './components/RecommendationCard';
import { EvaluationButtons } from './components/EvaluationButtons';
import { SessionStatus } from './components/SessionStatus';
import { HistoryView } from './components/HistoryView';

// Application interfaces
export interface AppConfig {
  apiBaseUrl: string;
  wsBaseUrl: string;
  debugMode: boolean;
  autoConnect: boolean;
}

export interface AppState {
  phase: 'loading' | 'upload' | 'session' | 'completed' | 'error';
  currentSessionId: string | null;
  errorMessage: string | null;
  isConnected: boolean;
  isLoading: boolean;
}

export interface PuzzleData {
  id: string;
  words: string[];
  uploadedFilename: string;
  createdAt: string;
}

export interface SessionData {
  id: string;
  puzzleId: string;
  status: 'active' | 'completed' | 'failed' | 'abandoned';
  solvedGroupsCount: number;
  remainingWords: string[];
  incorrectEvaluationCount: number;
  llmModel: string;
  pendingRecommendationId?: string;
}

export interface RecommendationData {
  id: string;
  sessionId: string;
  recommendedWords: string[];
  explanation: string;
  processingTimeMs: number;
  llmModel: string;
  timestamp: string;
  userEvaluation?: 'correct' | 'incorrect' | 'one_away';
}

export class App {
  private config: AppConfig;
  private state: AppState;
  private gameState: GameStateManager;
  private apiService: ApiService;
  private wsService: WebSocketService;
  
  // DOM elements
  private container: HTMLElement;
  private components: Map<string, any> = new Map();
  
  // Event handlers
  private eventHandlers: Map<string, Function[]> = new Map();

  constructor(containerId: string = 'app', config?: Partial<AppConfig>) {
    // Initialize configuration
    this.config = {
      apiBaseUrl: 'http://localhost:8000',
      wsBaseUrl: 'ws://localhost:8000',
      debugMode: false,
      autoConnect: true,
      ...config
    };

    // Initialize state
    this.state = {
      phase: 'loading',
      currentSessionId: null,
      errorMessage: null,
      isConnected: false,
      isLoading: false
    };

    // Get container element
    this.container = document.getElementById(containerId) as HTMLElement;
    if (!this.container) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }

    // Initialize services
    this.apiService = new ApiService(this.config.apiBaseUrl);
    this.gameState = new GameStateManager();
    this.wsService = webSocketService;
    
    // Setup service event handlers
    this.setupServiceHandlers();
  }

  /**
   * Initialize and start the application
   */
  public async init(): Promise<void> {
    try {
      this.log('Initializing NYT Connections Puzzle Assistant...');
      
      // Render initial UI
      this.renderUI();
      
      // Initialize components
      await this.initializeComponents();
      
      // Setup global event handlers
      this.setupGlobalHandlers();
      
      // Mark as ready
      this.setState({ phase: 'upload', isLoading: false });
      
      this.log('Application initialized successfully');
      
    } catch (error) {
      this.handleError('Failed to initialize application', error);
    }
  }

  /**
   * Handle file upload and puzzle creation
   */
  public async handleFileUpload(file: File): Promise<void> {
    try {
      this.setState({ isLoading: true });
      
      this.log('Uploading puzzle file:', file.name);
      
      // Upload file via API
      const puzzleData = await this.apiService.uploadPuzzle(file);
      
      // Update game state
      await this.gameState.setPuzzle(puzzleData);
      
      this.log('Puzzle uploaded successfully:', puzzleData.id);
      
      // Move to session creation
      await this.createSession(puzzleData.id);
      
    } catch (error) {
      this.handleError('Failed to upload puzzle', error);
    } finally {
      this.setState({ isLoading: false });
    }
  }

  /**
   * Create a new game session
   */
  public async createSession(puzzleId: string, llmModel: string = 'gpt-4'): Promise<void> {
    try {
      this.setState({ isLoading: true });
      
      this.log('Creating new session for puzzle:', puzzleId);
      
      // Create session via API
      const sessionData = await this.apiService.createSession(puzzleId, llmModel);
      
      // Update game state
      await this.gameState.setSession(sessionData);
      
      // Connect WebSocket
      if (this.config.autoConnect) {
        await this.connectWebSocket(sessionData.id);
      }
      
      this.setState({ 
        phase: 'session', 
        currentSessionId: sessionData.id 
      });
      
      this.log('Session created successfully:', sessionData.id);
      
    } catch (error) {
      this.handleError('Failed to create session', error);
    } finally {
      this.setState({ isLoading: false });
    }
  }

  /**
   * Connect to WebSocket for real-time updates
   */
  public async connectWebSocket(sessionId: string): Promise<void> {
    try {
      this.log('Connecting to WebSocket for session:', sessionId);
      
      await this.wsService.connect(sessionId);
      this.setState({ isConnected: true });
      
      this.log('WebSocket connected successfully');
      
    } catch (error) {
      this.handleError('Failed to connect WebSocket', error);
    }
  }

  /**
   * Request a new AI recommendation
   */
  public requestRecommendation(): void {
    if (!this.state.isConnected) {
      this.handleError('Cannot request recommendation - not connected', null);
      return;
    }

    this.log('Requesting new recommendation...');
    this.wsService.requestRecommendation();
  }

  /**
   * Evaluate a recommendation
   */
  public async evaluateRecommendation(
    recommendationId: string, 
    evaluation: 'correct' | 'incorrect' | 'one_away'
  ): Promise<void> {
    try {
      this.setState({ isLoading: true });
      
      this.log('Evaluating recommendation:', recommendationId, evaluation);
      
      // Send evaluation via API
      await this.apiService.evaluateRecommendation(
        this.state.currentSessionId!,
        recommendationId,
        evaluation
      );
      
      // Update game state
      await this.gameState.updateRecommendationEvaluation(recommendationId, evaluation);
      
      this.log('Recommendation evaluated successfully');
      
    } catch (error) {
      this.handleError('Failed to evaluate recommendation', error);
    } finally {
      this.setState({ isLoading: false });
    }
  }

  /**
   * End current session
   */
  public async endSession(): Promise<void> {
    try {
      this.log('Ending current session...');
      
      // Disconnect WebSocket
      this.wsService.disconnect();
      
      // Clear game state
      await this.gameState.reset();
      
      // Reset app state
      this.setState({
        phase: 'upload',
        currentSessionId: null,
        isConnected: false
      });
      
      this.log('Session ended successfully');
      
    } catch (error) {
      this.handleError('Error ending session', error);
    }
  }

  /**
   * Setup service event handlers
   */
  private setupServiceHandlers(): void {
    // WebSocket event handlers
    this.wsService.onSessionUpdate((sessionState) => {
      this.log('Session state updated:', sessionState);
      this.gameState.updateSessionState(sessionState);
      this.updateUIFromGameState();
    });

    this.wsService.onNewRecommendation((recommendation) => {
      this.log('New recommendation received:', recommendation);
      this.gameState.addRecommendation(recommendation);
      this.updateUIFromGameState();
    });

    this.wsService.onRecommendationUpdate((evaluation) => {
      this.log('Recommendation evaluation received:', evaluation);
      this.gameState.updateRecommendationEvaluation(evaluation.id, evaluation.userEvaluation);
      this.updateUIFromGameState();
    });

    this.wsService.onConnectionChange((status) => {
      this.log('WebSocket connection changed:', status.connected);
      this.setState({ isConnected: status.connected });
    });

    this.wsService.onError((errorData) => {
      this.handleError('WebSocket error', errorData.error);
    });

    // Game state event handlers
    this.gameState.onStateChange((newState) => {
      this.log('Game state changed:', newState);
      this.updateUIFromGameState();
    });
  }

  /**
   * Setup global event handlers
   */
  private setupGlobalHandlers(): void {
    // Handle browser window close
    window.addEventListener('beforeunload', () => {
      this.wsService.disconnect();
    });

    // Handle keyboard shortcuts
    document.addEventListener('keydown', (event) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'r':
            event.preventDefault();
            if (this.state.phase === 'session') {
              this.requestRecommendation();
            }
            break;
          case 'n':
            event.preventDefault();
            this.endSession();
            break;
        }
      }
    });
  }

  /**
   * Initialize UI components
   */
  private async initializeComponents(): Promise<void> {
    // Initialize each component based on current phase
    // This would normally instantiate the component classes
    
    this.log('Initializing UI components...');
    
    // For now, create placeholder component references
    this.components.set('fileUpload', new FileUpload());
    this.components.set('puzzleView', new PuzzleView());
    this.components.set('recommendationCard', new RecommendationCard());
    this.components.set('evaluationButtons', new EvaluationButtons());
    this.components.set('sessionStatus', new SessionStatus());
    this.components.set('historyView', new HistoryView());
  }

  /**
   * Render the main UI structure
   */
  private renderUI(): void {
    this.container.innerHTML = `
      <div class="app-container">
        <header class="app-header">
          <h1>NYT Connections Puzzle Assistant</h1>
          <div class="connection-status" id="connection-status">
            ${this.state.isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </div>
        </header>
        
        <main class="app-main" id="app-main">
          ${this.renderMainContent()}
        </main>
        
        <footer class="app-footer">
          <div class="debug-info" id="debug-info" style="display: ${this.config.debugMode ? 'block' : 'none'}">
            Phase: ${this.state.phase} | Session: ${this.state.currentSessionId || 'None'}
          </div>
        </footer>
      </div>
    `;
  }

  /**
   * Render main content based on current phase
   */
  private renderMainContent(): string {
    switch (this.state.phase) {
      case 'loading':
        return '<div class="loading">Loading...</div>';
      
      case 'upload':
        return `
          <div class="upload-section">
            <h2>Upload Puzzle</h2>
            <div id="file-upload"></div>
          </div>
        `;
      
      case 'session':
        return `
          <div class="session-section">
            <div id="session-status"></div>
            <div id="puzzle-view"></div>
            <div id="recommendation-area">
              <div id="recommendation-card"></div>
              <div id="evaluation-buttons"></div>
            </div>
            <div id="history-view"></div>
          </div>
        `;
      
      case 'completed':
        return '<div class="completed">Puzzle completed! 🎉</div>';
      
      case 'error':
        return `<div class="error">Error: ${this.state.errorMessage}</div>`;
      
      default:
        return '<div class="unknown-state">Unknown state</div>';
    }
  }

  /**
   * Update UI from current game state
   */
  private updateUIFromGameState(): void {
    // Update component states based on game state
    const gameState = this.gameState.getState();
    
    // Update each component with new data
    this.updateComponentStates(gameState);
    
    // Re-render if needed
    this.refreshUI();
  }

  /**
   * Update component states
   */
  private updateComponentStates(gameState: any): void {
    // Update each component based on game state
    // This would normally call update methods on component instances
    
    if (this.config.debugMode) {
      this.log('Updating component states with game state:', gameState);
    }
  }

  /**
   * Refresh the UI
   */
  private refreshUI(): void {
    // Update connection status
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
      statusElement.innerHTML = this.state.isConnected ? '🟢 Connected' : '🔴 Disconnected';
    }

    // Update debug info
    const debugElement = document.getElementById('debug-info');
    if (debugElement) {
      debugElement.innerHTML = `Phase: ${this.state.phase} | Session: ${this.state.currentSessionId || 'None'}`;
    }

    // Update loading states
    const elements = document.querySelectorAll('.loading-overlay');
    elements.forEach(el => {
      (el as HTMLElement).style.display = this.state.isLoading ? 'block' : 'none';
    });
  }

  /**
   * Update application state
   */
  private setState(newState: Partial<AppState>): void {
    this.state = { ...this.state, ...newState };
    this.refreshUI();
    this.emitEvent('stateChange', this.state);
  }

  /**
   * Handle errors
   */
  private handleError(message: string, error: any): void {
    console.error(message, error);
    
    this.setState({
      phase: 'error',
      errorMessage: typeof error === 'string' ? error : message,
      isLoading: false
    });
    
    this.emitEvent('error', { message, error });
  }

  /**
   * Logging utility
   */
  private log(...args: any[]): void {
    if (this.config.debugMode) {
      console.log('[App]', ...args);
    }
  }

  /**
   * Event system
   */
  public on(event: string, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  }

  public off(event: string, handler: Function): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private emitEvent(event: string, data: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  /**
   * Get current application state
   */
  public getState(): AppState {
    return { ...this.state };
  }

  /**
   * Get application configuration
   */
  public getConfig(): AppConfig {
    return { ...this.config };
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    this.wsService.disconnect();
    this.gameState.reset();
    this.eventHandlers.clear();
    this.components.clear();
  }
}

// Export singleton instance for easy use
export let appInstance: App | null = null;

/**
 * Initialize the application
 */
export async function initializeApp(containerId?: string, config?: Partial<AppConfig>): Promise<App> {
  if (appInstance) {
    console.warn('App already initialized');
    return appInstance;
  }

  appInstance = new App(containerId, config);
  await appInstance.init();
  
  return appInstance;
}

/**
 * Get the current app instance
 */
export function getApp(): App | null {
  return appInstance;
}

// Export for use in other modules
export default App;
