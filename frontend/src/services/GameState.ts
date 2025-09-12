/**
 * State management for game session in NYT Connections Puzzle Assistant.
 * 
 * This service provides centralized state management for the puzzle-solving session,
 * including puzzle data, session state, recommendations, and user interactions.
 */

export interface PuzzleState {
  id: string;
  words: string[];
  uploadedFilename: string;
  createdAt: string;
  userId?: string;
}

export interface SessionState {
  id: string;
  puzzleId: string;
  startTime: string;
  lastActivity: string;
  status: 'active' | 'completed' | 'failed' | 'abandoned';
  solvedGroupsCount: number;
  remainingWords: string[];
  incorrectEvaluationCount: number;
  llmModelConfig: string;
  pendingRecommendationId?: string;
}

export interface RecommendationState {
  id: string;
  sessionId: string;
  recommendedWords: string[];
  explanation: string;
  timestamp: string;
  userEvaluation?: 'correct' | 'incorrect' | 'one_away';
  evaluationTimestamp?: string;
  llmModel: string;
  processingTimeMs: number;
}

export interface SolvedGroup {
  theme: string;
  words: string[];
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
  solvedAt: string;
}

export interface GameState {
  // Core data
  puzzle: PuzzleState | null;
  session: SessionState | null;
  
  // Recommendations
  recommendations: RecommendationState[];
  currentRecommendation: RecommendationState | null;
  
  // Game progress
  solvedGroups: SolvedGroup[];
  incorrectAttempts: string[][];
  oneAwayAttempts: string[][];
  
  // UI state
  isLoading: boolean;
  isConnected: boolean;
  errorMessage: string | null;
  
  // Metadata
  lastUpdated: string;
  totalProcessingTime: number;
}

export type GameStateEventType = 
  | 'stateChange'
  | 'puzzleSet'
  | 'sessionSet'
  | 'recommendationAdded'
  | 'recommendationEvaluated'
  | 'groupSolved'
  | 'gameCompleted'
  | 'error';

export type GameStateEventHandler = (data: any) => void;

export class GameStateManager {
  private state: GameState;
  private eventHandlers: Map<GameStateEventType, GameStateEventHandler[]> = new Map();
  private readonly maxRecommendations = 50; // Limit history size

  constructor() {
    this.state = this.getInitialState();
  }

  /**
   * Get initial state
   */
  private getInitialState(): GameState {
    return {
      puzzle: null,
      session: null,
      recommendations: [],
      currentRecommendation: null,
      solvedGroups: [],
      incorrectAttempts: [],
      oneAwayAttempts: [],
      isLoading: false,
      isConnected: false,
      errorMessage: null,
      lastUpdated: new Date().toISOString(),
      totalProcessingTime: 0
    };
  }

  /**
   * Get current state (immutable copy)
   */
  public getState(): GameState {
    return JSON.parse(JSON.stringify(this.state));
  }

  /**
   * Set puzzle data
   */
  public async setPuzzle(puzzleData: PuzzleState): Promise<void> {
    this.updateState({
      puzzle: puzzleData,
      lastUpdated: new Date().toISOString()
    });
    
    this.emitEvent('puzzleSet', puzzleData);
  }

  /**
   * Set session data
   */
  public async setSession(sessionData: SessionState): Promise<void> {
    this.updateState({
      session: sessionData,
      lastUpdated: new Date().toISOString()
    });
    
    this.emitEvent('sessionSet', sessionData);
  }

  /**
   * Update session state (from WebSocket updates)
   */
  public updateSessionState(sessionUpdate: Partial<SessionState>): void {
    if (!this.state.session) {
      console.warn('Cannot update session state: no active session');
      return;
    }

    const updatedSession = {
      ...this.state.session,
      ...sessionUpdate,
      lastActivity: new Date().toISOString()
    };

    this.updateState({
      session: updatedSession,
      lastUpdated: new Date().toISOString()
    });
  }

  /**
   * Add a new recommendation
   */
  public addRecommendation(recommendation: RecommendationState): void {
    const recommendations = [...this.state.recommendations];
    
    // Limit recommendation history
    if (recommendations.length >= this.maxRecommendations) {
      recommendations.shift(); // Remove oldest
    }
    
    recommendations.push(recommendation);

    this.updateState({
      recommendations,
      currentRecommendation: recommendation,
      totalProcessingTime: this.state.totalProcessingTime + recommendation.processingTimeMs,
      lastUpdated: new Date().toISOString()
    });

    this.emitEvent('recommendationAdded', recommendation);
  }

  /**
   * Update recommendation evaluation
   */
  public updateRecommendationEvaluation(
    recommendationId: string, 
    evaluation: 'correct' | 'incorrect' | 'one_away'
  ): void {
    const recommendations = this.state.recommendations.map(rec => {
      if (rec.id === recommendationId) {
        return {
          ...rec,
          userEvaluation: evaluation,
          evaluationTimestamp: new Date().toISOString()
        };
      }
      return rec;
    });

    // Update current recommendation if it matches
    let currentRecommendation = this.state.currentRecommendation;
    if (currentRecommendation && currentRecommendation.id === recommendationId) {
      currentRecommendation = {
        ...currentRecommendation,
        userEvaluation: evaluation,
        evaluationTimestamp: new Date().toISOString()
      };
    }

    // Update attempt tracking
    const recommendation = recommendations.find(r => r.id === recommendationId);
    if (recommendation) {
      this.updateAttemptHistory(recommendation, evaluation);
    }

    this.updateState({
      recommendations,
      currentRecommendation,
      lastUpdated: new Date().toISOString()
    });

    this.emitEvent('recommendationEvaluated', { recommendationId, evaluation });

    // Check if game is completed
    if (evaluation === 'correct') {
      this.handleCorrectEvaluation(recommendation!);
    }
  }

  /**
   * Handle correct evaluation
   */
  private handleCorrectEvaluation(recommendation: RecommendationState): void {
    // Add to solved groups (in a real app, this would come from the session update)
    const newGroup: SolvedGroup = {
      theme: 'Auto-detected theme', // This would come from the backend
      words: recommendation.recommendedWords,
      difficulty: 'medium', // This would be determined by the backend
      solvedAt: new Date().toISOString()
    };

    const solvedGroups = [...this.state.solvedGroups, newGroup];
    
    // Update remaining words
    let remainingWords = [...(this.state.session?.remainingWords || [])];
    recommendation.recommendedWords.forEach(word => {
      remainingWords = remainingWords.filter(w => w !== word);
    });

    // Update session if exists
    let session = this.state.session;
    if (session) {
      session = {
        ...session,
        remainingWords,
        solvedGroupsCount: solvedGroups.length,
        lastActivity: new Date().toISOString()
      };

      // Check if game is completed (all 4 groups solved)
      if (solvedGroups.length >= 4) {
        session.status = 'completed';
        this.emitEvent('gameCompleted', { solvedGroups, session });
      }
    }

    this.updateState({
      solvedGroups,
      session,
      lastUpdated: new Date().toISOString()
    });

    this.emitEvent('groupSolved', newGroup);
  }

  /**
   * Update attempt history tracking
   */
  private updateAttemptHistory(
    recommendation: RecommendationState, 
    evaluation: 'correct' | 'incorrect' | 'one_away'
  ): void {
    if (evaluation === 'incorrect') {
      this.updateState({
        incorrectAttempts: [...this.state.incorrectAttempts, recommendation.recommendedWords]
      });
    } else if (evaluation === 'one_away') {
      this.updateState({
        oneAwayAttempts: [...this.state.oneAwayAttempts, recommendation.recommendedWords]
      });
    }
  }

  /**
   * Set loading state
   */
  public setLoading(isLoading: boolean): void {
    this.updateState({
      isLoading,
      lastUpdated: new Date().toISOString()
    });
  }

  /**
   * Set connection state
   */
  public setConnected(isConnected: boolean): void {
    this.updateState({
      isConnected,
      lastUpdated: new Date().toISOString()
    });
  }

  /**
   * Set error message
   */
  public setError(errorMessage: string | null): void {
    this.updateState({
      errorMessage,
      lastUpdated: new Date().toISOString()
    });

    if (errorMessage) {
      this.emitEvent('error', { message: errorMessage });
    }
  }

  /**
   * Get game statistics
   */
  public getGameStats(): {
    totalRecommendations: number;
    correctRecommendations: number;
    incorrectRecommendations: number;
    oneAwayRecommendations: number;
    averageProcessingTime: number;
    solvedGroupsCount: number;
    gameProgress: number;
  } {
    const totalRecommendations = this.state.recommendations.length;
    const correctRecommendations = this.state.recommendations.filter(r => r.userEvaluation === 'correct').length;
    const incorrectRecommendations = this.state.recommendations.filter(r => r.userEvaluation === 'incorrect').length;
    const oneAwayRecommendations = this.state.recommendations.filter(r => r.userEvaluation === 'one_away').length;
    
    const averageProcessingTime = totalRecommendations > 0 
      ? this.state.totalProcessingTime / totalRecommendations 
      : 0;

    const solvedGroupsCount = this.state.solvedGroups.length;
    const gameProgress = (solvedGroupsCount / 4) * 100; // 4 groups total

    return {
      totalRecommendations,
      correctRecommendations,
      incorrectRecommendations,
      oneAwayRecommendations,
      averageProcessingTime,
      solvedGroupsCount,
      gameProgress
    };
  }

  /**
   * Get recommendation history
   */
  public getRecommendationHistory(): RecommendationState[] {
    return [...this.state.recommendations];
  }

  /**
   * Get current recommendation
   */
  public getCurrentRecommendation(): RecommendationState | null {
    return this.state.currentRecommendation;
  }

  /**
   * Get solved groups
   */
  public getSolvedGroups(): SolvedGroup[] {
    return [...this.state.solvedGroups];
  }

  /**
   * Get remaining words
   */
  public getRemainingWords(): string[] {
    return this.state.session?.remainingWords || [];
  }

  /**
   * Check if game is active
   */
  public isGameActive(): boolean {
    return this.state.session?.status === 'active';
  }

  /**
   * Check if game is completed
   */
  public isGameCompleted(): boolean {
    return this.state.session?.status === 'completed' || this.state.solvedGroups.length >= 4;
  }

  /**
   * Reset game state
   */
  public async reset(): Promise<void> {
    this.state = this.getInitialState();
    this.emitEvent('stateChange', this.state);
  }

  /**
   * Export state for persistence
   */
  public exportState(): string {
    return JSON.stringify(this.state);
  }

  /**
   * Import state from persistence
   */
  public importState(stateJson: string): void {
    try {
      const importedState = JSON.parse(stateJson);
      this.state = {
        ...this.getInitialState(),
        ...importedState,
        lastUpdated: new Date().toISOString()
      };
      this.emitEvent('stateChange', this.state);
    } catch (error) {
      console.error('Failed to import state:', error);
      this.setError('Failed to restore game state');
    }
  }

  /**
   * Subscribe to state change events
   */
  public onStateChange(handler: GameStateEventHandler): void {
    this.on('stateChange', handler);
  }

  /**
   * Subscribe to specific events
   */
  public on(event: GameStateEventType, handler: GameStateEventHandler): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  }

  /**
   * Unsubscribe from events
   */
  public off(event: GameStateEventType, handler: GameStateEventHandler): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Update state and emit change event
   */
  private updateState(partialState: Partial<GameState>): void {
    this.state = {
      ...this.state,
      ...partialState
    };
    
    this.emitEvent('stateChange', this.state);
  }

  /**
   * Emit an event to all registered handlers
   */
  private emitEvent(event: GameStateEventType, data: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
  }
}

// Create and export singleton instance
export const gameStateManager = new GameStateManager();

// Export for custom instances
export default GameStateManager;
