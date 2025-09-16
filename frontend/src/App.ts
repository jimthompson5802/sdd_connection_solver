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
      
      // Setup global event handlers (includes UI handlers)
      this.setupGlobalHandlers();
      
      // Mark as ready
      this.setState({ phase: 'upload', isLoading: false });
      
      this.log('Application initialized successfully');
      // Mark the app as ready for E2E tests to wait on
      const appRoot = document.getElementById('app');
      if (appRoot) {
        appRoot.setAttribute('data-app-ready', 'true');
      }
      
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

    // Setup UI event handlers for new layout
    this.setupUIEventHandlers();
  }

  /**
   * Setup event handlers for UI elements
   */
  private setupUIEventHandlers(): void {
    // Setup puzzle file input handler
    const setupButton = document.getElementById('setup-puzzle-btn') as HTMLButtonElement;
    if (setupButton) {
      setupButton.addEventListener('click', () => {
        const fileInput = document.getElementById('puzzle-file-input') as HTMLInputElement;
        if (fileInput && fileInput.files && fileInput.files[0]) {
          this.handleFileUpload(fileInput.files[0]);
        }
      });
    }

    // Setup recommendation button handler
    const getRecommendationBtn = document.getElementById('get-recommendation-btn') as HTMLButtonElement;
    if (getRecommendationBtn) {
      getRecommendationBtn.addEventListener('click', () => {
        this.requestRecommendation();
      });
    }

    // Setup terminate button handler
    const terminateBtn = document.getElementById('terminate-btn') as HTMLButtonElement;
    if (terminateBtn) {
      terminateBtn.addEventListener('click', () => {
        this.endSession();
      });
    }

    // Setup color buttons handlers
    const colorButtons = document.querySelectorAll('.color-btn');
    colorButtons.forEach(button => {
      button.addEventListener('click', (event) => {
        const target = event.target as HTMLButtonElement;
        const color = target.getAttribute('data-color');
        this.selectGroupColor(color);
      });
    });

    // Setup response buttons handlers
    const responseButtons = document.querySelectorAll('.response-btn');
    responseButtons.forEach(button => {
      button.addEventListener('click', (event) => {
        const target = event.target as HTMLButtonElement;
        const response = target.getAttribute('data-response');
        this.selectPuzzleResponse(response);
      });
    });
  }

  /**
   * Handle group color selection
   */
  private selectGroupColor(color: string | null): void {
    // Remove previous selection
    document.querySelectorAll('.color-btn').forEach(btn => btn.classList.remove('selected'));
    
    // Add selection to clicked button
    if (color) {
      const button = document.querySelector(`[data-color="${color}"]`);
      if (button) {
        button.classList.add('selected');
      }
    }
    
    this.log('Group color selected:', color);
  }

  /**
   * Handle puzzle response selection
   */
  private selectPuzzleResponse(response: string | null): void {
    // Remove previous selection
    document.querySelectorAll('.response-btn').forEach(btn => btn.classList.remove('selected'));
    
    // Add selection to clicked button
    if (response) {
      const button = document.querySelector(`[data-response="${response}"]`);
      if (button) {
        button.classList.add('selected');
      }
      
      // Process the response
      this.processPuzzleResponse(response);
    }
    
    this.log('Puzzle response selected:', response);
  }

  /**
   * Process puzzle response (evaluation)
   */
  private async processPuzzleResponse(response: string): Promise<void> {
    const gameState = this.gameState.getState();
    if (gameState.session?.pendingRecommendationId) {
      let evaluation: 'correct' | 'incorrect' | 'one_away';
      
      switch (response) {
        case 'one-away':
          evaluation = 'one_away';
          break;
        case 'not-correct':
          evaluation = 'incorrect';
          break;
        default:
          return;
      }
      
      await this.evaluateRecommendation(gameState.session.pendingRecommendationId, evaluation);
    }
  }

  /**
   * Initialize UI components
   */
  private async initializeComponents(): Promise<void> {
    // Initialize each component based on current phase
    // This would normally instantiate the component classes
    
    this.log('Initializing UI components...');
    
    // For now, create placeholder component references
    this.components.set('fileUpload', new FileUpload('file-upload'));
    this.components.set('puzzleView', new PuzzleView('puzzle-view'));
    this.components.set('recommendationCard', new RecommendationCard('recommendation-card'));
    this.components.set('evaluationButtons', new EvaluationButtons('evaluation-buttons'));
    this.components.set('sessionStatus', new SessionStatus('session-status'));
    this.components.set('historyView', new HistoryView('history-view'));
  }

  /**
   * Render the main UI structure
   */
  private renderUI(): void {
    // Since HTML structure is now static in index.html, 
    // we just need to set up initial UI state
    this.initializeUIElements();
  }

  /**
   * Initialize UI elements with default values
   */
  private initializeUIElements(): void {
    // Set initial values for UI elements
    const foundCountInput = document.getElementById('found-count') as HTMLInputElement;
    if (foundCountInput) foundCountInput.value = '0';

    const mistakeCountInput = document.getElementById('mistake-count') as HTMLInputElement;
    if (mistakeCountInput) mistakeCountInput.value = '0';

    const statusInput = document.getElementById('status-display') as HTMLInputElement;
    if (statusInput) statusInput.value = 'Ready';

    // Clear text areas
    const remainingWords = document.getElementById('remaining-words') as HTMLTextAreaElement;
    if (remainingWords) remainingWords.value = '';

    const recommendedGroup = document.getElementById('recommended-group') as HTMLTextAreaElement;
    if (recommendedGroup) recommendedGroup.value = '';

    const connectionReason = document.getElementById('connection-reason') as HTMLTextAreaElement;
    if (connectionReason) connectionReason.value = '';

    const recommenderInfo = document.getElementById('recommender-info') as HTMLTextAreaElement;
    if (recommenderInfo) recommenderInfo.value = '';
  }

  /**
   * Update UI elements based on game state
   */
  private updateUIElements(): void {
    const gameState = this.gameState.getState();
    
    // Update counters
    const foundCountInput = document.getElementById('found-count') as HTMLInputElement;
    if (foundCountInput && gameState.session) {
      foundCountInput.value = gameState.session.solvedGroupsCount.toString();
    }

    const mistakeCountInput = document.getElementById('mistake-count') as HTMLInputElement;
    if (mistakeCountInput && gameState.session) {
      mistakeCountInput.value = gameState.session.incorrectEvaluationCount.toString();
    }

    // Update remaining words
    const remainingWords = document.getElementById('remaining-words') as HTMLTextAreaElement;
    if (remainingWords && gameState.session) {
      remainingWords.value = gameState.session.remainingWords.join(', ');
    }

    // Update status
    const statusInput = document.getElementById('status-display') as HTMLInputElement;
    if (statusInput && gameState.session) {
      statusInput.value = gameState.session.status;
    }

    // Update current recommendation if available
    if (gameState.currentRecommendation) {
      const recommendedGroup = document.getElementById('recommended-group') as HTMLTextAreaElement;
      if (recommendedGroup) {
        recommendedGroup.value = gameState.currentRecommendation.recommendedWords.join(', ');
      }

      const connectionReason = document.getElementById('connection-reason') as HTMLTextAreaElement;
      if (connectionReason) {
        connectionReason.value = gameState.currentRecommendation.explanation;
      }

      const recommenderInfo = document.getElementById('recommender-info') as HTMLTextAreaElement;
      if (recommenderInfo) {
        recommenderInfo.value = `Model: ${gameState.currentRecommendation.llmModel}\nProcessing Time: ${gameState.currentRecommendation.processingTimeMs}ms`;
      }
    }

    // Enable/disable buttons based on state
    this.updateButtonStates();
  }

  /**
   * Update button states based on current game state
   */
  private updateButtonStates(): void {
    const gameState = this.gameState.getState();
    
    const setupButton = document.getElementById('setup-puzzle-btn') as HTMLButtonElement;
    if (setupButton) {
      setupButton.disabled = this.state.isLoading || this.state.phase === 'session';
    }

    const getRecommendationBtn = document.getElementById('get-recommendation-btn') as HTMLButtonElement;
    if (getRecommendationBtn) {
      getRecommendationBtn.disabled = this.state.isLoading || 
                                     this.state.phase !== 'session' || 
                                     !this.state.isConnected;
    }

    const terminateBtn = document.getElementById('terminate-btn') as HTMLButtonElement;
    if (terminateBtn) {
      terminateBtn.disabled = this.state.phase !== 'session';
    }

    // Enable/disable response buttons based on whether there's a current recommendation
    const responseButtons = document.querySelectorAll('.response-btn') as NodeListOf<HTMLButtonElement>;
    responseButtons.forEach(button => {
      button.disabled = !gameState.currentRecommendation;
    });
  }

  /**
   * Update UI from current game state
   */
  private updateUIFromGameState(): void {
    // Update component states based on game state
    const gameState = this.gameState.getState();
    
    // Update UI elements with new data
    this.updateUIElements();
    
    // Update component states
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
    // Update loading states
    const elements = document.querySelectorAll('.loading-overlay');
    elements.forEach(el => {
      (el as HTMLElement).style.display = this.state.isLoading ? 'block' : 'none';
    });

    // Update button states
    this.updateButtonStates();

    // Show/hide sections based on phase
    const puzzleInterface = document.querySelector('.puzzle-interface') as HTMLElement;
    if (puzzleInterface) {
      puzzleInterface.style.display = this.state.phase === 'error' ? 'none' : 'block';
    }

    // Show error message if in error state
    if (this.state.phase === 'error') {
      const statusInput = document.getElementById('status-display') as HTMLInputElement;
      if (statusInput) {
        statusInput.value = this.state.errorMessage || 'Error occurred';
      }
    }
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
    const appRoot = document.getElementById('app');
    if (appRoot) {
      appRoot.removeAttribute('data-app-ready');
    }
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
