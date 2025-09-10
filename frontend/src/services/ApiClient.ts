/**
 * HTTP API client for the NYT Connections Puzzle Assistant backend
 */

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface PuzzleData {
  id: string;
  words: string[];
  created_at: string;
}

export interface SessionData {
  id: string;
  puzzle_id: string;
  llm_model: string;
  created_at: string;
  status: 'active' | 'completed';
}

export interface RecommendationData {
  id: string;
  words: string[];
  category: string;
  confidence: number;
  reasoning: string;
  created_at: string;
  status: 'pending' | 'evaluated';
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl;
  }

  /**
   * Upload a puzzle file
   */
  public async uploadPuzzle(file: File): Promise<ApiResponse<PuzzleData>> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${this.baseUrl}/puzzles/upload`, {
        method: 'POST',
        body: formData,
      });

      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Upload failed',
      };
    }
  }

  /**
   * Get puzzle by ID
   */
  public async getPuzzle(puzzleId: string): Promise<ApiResponse<PuzzleData>> {
    try {
      const response = await fetch(`${this.baseUrl}/puzzles/${puzzleId}`);
      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get puzzle',
      };
    }
  }

  /**
   * Create a new session
   */
  public async createSession(puzzleId: string, llmModel: string): Promise<ApiResponse<SessionData>> {
    try {
      const response = await fetch(`${this.baseUrl}/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          puzzle_id: puzzleId,
          llm_model: llmModel,
        }),
      });

      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create session',
      };
    }
  }

  /**
   * Get session by ID
   */
  public async getSession(sessionId: string): Promise<ApiResponse<SessionData>> {
    try {
      const response = await fetch(`${this.baseUrl}/sessions/${sessionId}`);
      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get session',
      };
    }
  }

  /**
   * Generate recommendations for a session
   */
  public async generateRecommendations(sessionId: string, context?: string): Promise<ApiResponse<RecommendationData[]>> {
    try {
      const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          context: context || '',
        }),
      });

      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to generate recommendations',
      };
    }
  }

  /**
   * Get recommendations for a session
   */
  public async getRecommendations(sessionId: string): Promise<ApiResponse<RecommendationData[]>> {
    try {
      const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/recommendations`);
      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get recommendations',
      };
    }
  }

  /**
   * Evaluate a recommendation
   */
  public async evaluateRecommendation(
    sessionId: string,
    recommendationId: string,
    evaluation: 'correct' | 'incorrect' | 'one_away'
  ): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(
        `${this.baseUrl}/sessions/${sessionId}/recommendations/${recommendationId}/evaluate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            evaluation,
          }),
        }
      );

      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to evaluate recommendation',
      };
    }
  }

  /**
   * Get session history
   */
  public async getSessionHistory(sessionId: string): Promise<ApiResponse<unknown[]>> {
    try {
      const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/history`);
      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get session history',
      };
    }
  }
}

// Singleton instance for the application
export const apiClient = new ApiClient();
