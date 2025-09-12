/**
 * Example usage of WebSocketService for NYT Connections Puzzle Assistant
 * 
 * This example demonstrates how to integrate the WebSocket service
 * into a puzzle-solving component.
 */

import { webSocketService, SessionState, Recommendation } from './WebSocketService';

export class PuzzleGameExample {
  private currentSessionId: string | null = null;

  constructor() {
    this.setupWebSocketHandlers();
  }

  /**
   * Start a new puzzle session with WebSocket connectivity
   */
  public async startSession(sessionId: string): Promise<void> {
    try {
      // Connect to WebSocket for this session
      await webSocketService.connect(sessionId);
      this.currentSessionId = sessionId;
      console.log('Connected to session:', sessionId);
    } catch (error) {
      console.error('Failed to connect to session:', error);
      throw error;
    }
  }

  /**
   * Request a new AI recommendation
   */
  public requestRecommendation(): void {
    if (!webSocketService.isConnected) {
      throw new Error('WebSocket not connected');
    }
    
    console.log('Requesting new recommendation...');
    webSocketService.requestRecommendation();
  }

  /**
   * End the current session
   */
  public endSession(): void {
    webSocketService.disconnect();
    this.currentSessionId = null;
    console.log('Session ended');
  }

  private setupWebSocketHandlers(): void {
    // Handle session state updates
    webSocketService.onSessionUpdate((sessionState: SessionState) => {
      console.log('Session state updated:', sessionState);
      this.updateUI(sessionState);
    });

    // Handle new recommendations
    webSocketService.onNewRecommendation((recommendation: Recommendation) => {
      console.log('New recommendation received:', recommendation);
      this.displayRecommendation(recommendation);
    });

    // Handle recommendation evaluation updates
    webSocketService.onRecommendationUpdate((evaluation) => {
      console.log('Recommendation evaluation updated:', evaluation);
      this.updateRecommendationStatus(evaluation);
    });

    // Handle recommendation request acknowledgments
    webSocketService.onRecommendationRequestReceived((data) => {
      console.log('Recommendation request received by server at:', data.timestamp);
      this.showLoadingIndicator();
    });

    // Handle connection status changes
    webSocketService.onConnectionChange((status) => {
      console.log('Connection status changed:', status);
      this.updateConnectionStatus(status.connected);
    });

    // Handle errors
    webSocketService.onError((errorData) => {
      console.error('WebSocket error:', errorData);
      this.showError(errorData.error);
    });
  }

  private updateUI(sessionState: SessionState): void {
    // Update puzzle UI with current session state
    console.log('Updating UI with session state');
    console.log('- Status:', sessionState.status);
    console.log('- Solved groups:', sessionState.solvedGroupsCount);
    console.log('- Remaining words:', sessionState.remainingWords.length);
    console.log('- Incorrect evaluations:', sessionState.incorrectEvaluationCount);
  }

  private displayRecommendation(recommendation: Recommendation): void {
    // Display the new recommendation in the UI
    console.log('Displaying recommendation:');
    console.log('- Words:', recommendation.recommendedWords.join(', '));
    console.log('- Explanation:', recommendation.explanation);
    console.log('- Model:', recommendation.llmModel);
    console.log('- Processing time:', recommendation.processingTimeMs + 'ms');
    
    this.hideLoadingIndicator();
  }

  private updateRecommendationStatus(evaluation: any): void {
    // Update the recommendation UI with evaluation result
    console.log('Updating recommendation status with evaluation:', evaluation.userEvaluation);
  }

  private showLoadingIndicator(): void {
    console.log('Showing loading indicator...');
  }

  private hideLoadingIndicator(): void {
    console.log('Hiding loading indicator...');
  }

  private updateConnectionStatus(connected: boolean): void {
    console.log('Connection status:', connected ? 'Connected' : 'Disconnected');
  }

  private showError(error: string): void {
    console.error('Showing error to user:', error);
  }
}

// Example usage
export async function exampleUsage(): Promise<void> {
  const puzzleGame = new PuzzleGameExample();
  
  try {
    // Start session
    await puzzleGame.startSession('example-session-123');
    
    // Request recommendations
    setTimeout(() => {
      puzzleGame.requestRecommendation();
    }, 1000);
    
    // End session after 30 seconds
    setTimeout(() => {
      puzzleGame.endSession();
    }, 30000);
    
  } catch (error) {
    console.error('Example failed:', error);
  }
}
