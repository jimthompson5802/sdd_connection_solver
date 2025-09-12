/**
 * API service layer for HTTP requests to the NYT Connections Puzzle Assistant backend.
 * 
 * This service provides a high-level interface for all backend API communication,
 * including error handling, request/response transformation, and type safety.
 */

export interface PuzzleUploadResponse {
  id: string;
  words: string[];
  uploadedFilename: string;
  createdAt: string;
  userId?: string;
}

export interface CreateSessionRequest {
  puzzleId: string;
  llmModel: string;
  userId?: string;
}

export interface SessionResponse {
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

export interface RecommendationResponse {
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

export interface EvaluateRecommendationRequest {
  evaluation: 'correct' | 'incorrect' | 'one_away';
}

export interface HistoryResponse {
  sessionId: string;
  recommendations: RecommendationResponse[];
  totalCount: number;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: any;
}

export class ApiError extends Error {
  public statusCode: number;
  public response?: ErrorResponse;

  constructor(message: string, statusCode: number, response?: ErrorResponse) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

export class ApiService {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseUrl: string = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  /**
   * Upload a puzzle file
   */
  public async uploadPuzzle(file: File, userId?: string): Promise<PuzzleUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (userId) {
      formData.append('user_id', userId);
    }

    const response = await this.request('/puzzles/upload', {
      method: 'POST',
      body: formData,
      headers: {} // Don't set Content-Type for FormData
    });

    return this.handleResponse<PuzzleUploadResponse>(response);
  }

  /**
   * Get puzzle by ID
   */
  public async getPuzzle(puzzleId: string): Promise<PuzzleUploadResponse> {
    const response = await this.request(`/puzzles/${puzzleId}`, {
      method: 'GET'
    });

    return this.handleResponse<PuzzleUploadResponse>(response);
  }

  /**
   * Create a new session
   */
  public async createSession(puzzleId: string, llmModel: string, userId?: string): Promise<SessionResponse> {
    const requestData: CreateSessionRequest = {
      puzzleId,
      llmModel,
      ...(userId && { userId })
    };

    const response = await this.request('/sessions', {
      method: 'POST',
      body: JSON.stringify(requestData)
    });

    return this.handleResponse<SessionResponse>(response);
  }

  /**
   * Get session by ID
   */
  public async getSession(sessionId: string): Promise<SessionResponse> {
    const response = await this.request(`/sessions/${sessionId}`, {
      method: 'GET'
    });

    return this.handleResponse<SessionResponse>(response);
  }

  /**
   * Request a new recommendation
   */
  public async requestRecommendation(sessionId: string): Promise<RecommendationResponse> {
    const response = await this.request(`/sessions/${sessionId}/recommendations`, {
      method: 'POST'
    });

    return this.handleResponse<RecommendationResponse>(response);
  }

  /**
   * Get recommendations for a session
   */
  public async getRecommendations(sessionId: string): Promise<RecommendationResponse[]> {
    const response = await this.request(`/sessions/${sessionId}/recommendations`, {
      method: 'GET'
    });

    const data = await this.handleResponse<{ recommendations: RecommendationResponse[] }>(response);
    return data.recommendations;
  }

  /**
   * Evaluate a recommendation
   */
  public async evaluateRecommendation(
    sessionId: string,
    recommendationId: string,
    evaluation: 'correct' | 'incorrect' | 'one_away'
  ): Promise<RecommendationResponse> {
    const requestData: EvaluateRecommendationRequest = {
      evaluation
    };

    const response = await this.request(
      `/sessions/${sessionId}/recommendations/${recommendationId}/evaluate`,
      {
        method: 'POST',
        body: JSON.stringify(requestData)
      }
    );

    return this.handleResponse<RecommendationResponse>(response);
  }

  /**
   * Get session history
   */
  public async getSessionHistory(sessionId: string): Promise<HistoryResponse> {
    const response = await this.request(`/sessions/${sessionId}/history`, {
      method: 'GET'
    });

    return this.handleResponse<HistoryResponse>(response);
  }

  /**
   * Health check
   */
  public async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.request('/health', {
      method: 'GET'
    });

    return this.handleResponse<{ status: string; timestamp: string }>(response);
  }

  /**
   * Make HTTP request with error handling
   */
  private async request(endpoint: string, options: RequestInit): Promise<Response> {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Merge headers, but don't override Content-Type if already set to empty (for FormData)
    const headers: Record<string, string> = {
      ...this.defaultHeaders,
      ...(options.headers as Record<string, string>)
    };

    // Remove Content-Type if it's an empty object (for FormData)
    if (options.headers && Object.keys(options.headers).length === 0) {
      delete headers['Content-Type'];
    }

    const requestOptions: RequestInit = {
      ...options,
      headers
    };

    try {
      console.log(`API Request: ${options.method} ${url}`);
      
      const response = await fetch(url, requestOptions);
      
      console.log(`API Response: ${response.status} ${response.statusText}`);
      
      return response;
      
    } catch (error) {
      console.error('API Request failed:', error);
      throw new ApiError(
        `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        0
      );
    }
  }

  /**
   * Handle API response with error checking
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    let responseData: any;
    
    try {
      const textResponse = await response.text();
      responseData = textResponse ? JSON.parse(textResponse) : {};
    } catch (error) {
      throw new ApiError(
        'Failed to parse response JSON',
        response.status
      );
    }

    if (!response.ok) {
      const errorResponse: ErrorResponse = responseData;
      throw new ApiError(
        errorResponse.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorResponse
      );
    }

    return responseData as T;
  }

  /**
   * Set authorization token
   */
  public setAuthToken(token: string): void {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  /**
   * Remove authorization token
   */
  public clearAuthToken(): void {
    delete this.defaultHeaders['Authorization'];
  }

  /**
   * Set custom header
   */
  public setHeader(key: string, value: string): void {
    this.defaultHeaders[key] = value;
  }

  /**
   * Remove custom header
   */
  public removeHeader(key: string): void {
    delete this.defaultHeaders[key];
  }

  /**
   * Get current base URL
   */
  public getBaseUrl(): string {
    return this.baseUrl;
  }

  /**
   * Update base URL
   */
  public setBaseUrl(baseUrl: string): void {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }
}

// Create and export singleton instance
export const apiService = new ApiService();

// Export for custom instances
export default ApiService;
