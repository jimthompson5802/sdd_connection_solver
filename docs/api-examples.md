# NYT Connections Puzzle Assistant - API Examples

**Version**: 1.0.0  
**Last Updated**: September 12, 2025  
**Base URL**: `http://localhost:8000`

This document provides comprehensive examples for all API endpoints in the NYT Connections Puzzle Assistant web application.

## Table of Contents

1. [Authentication & Headers](#authentication--headers)
2. [Puzzle Management](#puzzle-management)
3. [Session Management](#session-management)
4. [AI Recommendations](#ai-recommendations)
5. [History & Analytics](#history--analytics)
6. [WebSocket Real-time Communication](#websocket-real-time-communication)
7. [Health Check Endpoints](#health-check-endpoints)
8. [Error Handling](#error-handling)

## Authentication & Headers

Currently, the API does not require authentication for development. All requests should include:

```bash
Content-Type: application/json
```

For file uploads, use:
```bash
Content-Type: multipart/form-data
```

## Puzzle Management

### Upload Puzzle File

Create a new puzzle by uploading a text file containing 16 comma-separated words.

**Endpoint:** `POST /api/v1/puzzles/upload`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/puzzles/upload \
  -F "file=@puzzle_words.txt" \
  -F "user_id=user-123"
```

**Example puzzle_words.txt content:**
```
BASS,PIANO,GUITAR,DRUMS,SALMON,TUNA,COD,TROUT,YELLOW,BLUE,RED,GREEN,APPLE,ORANGE,BANANA,GRAPE
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "words": [
    "BASS", "PIANO", "GUITAR", "DRUMS",
    "SALMON", "TUNA", "COD", "TROUT", 
    "YELLOW", "BLUE", "RED", "GREEN",
    "APPLE", "ORANGE", "BANANA", "GRAPE"
  ],
  "uploaded_filename": "puzzle_words.txt",
  "created_at": "2025-09-12T14:30:00Z",
  "user_id": "user-123"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "File must contain exactly 16 comma-separated words",
  "details": {
    "word_count": 14,
    "expected": 16
  }
}
```

### Get Puzzle Details

Retrieve information about a specific puzzle.

**Endpoint:** `GET /api/v1/puzzles/{puzzle_id}`

**Request:**
```bash
curl http://localhost:8000/api/v1/puzzles/550e8400-e29b-41d4-a716-446655440001
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "words": [
    "BASS", "PIANO", "GUITAR", "DRUMS",
    "SALMON", "TUNA", "COD", "TROUT", 
    "YELLOW", "BLUE", "RED", "GREEN",
    "APPLE", "ORANGE", "BANANA", "GRAPE"
  ],
  "uploaded_filename": "puzzle_words.txt",
  "created_at": "2025-09-12T14:30:00Z",
  "user_id": "user-123"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "NOT_FOUND",
  "message": "Puzzle with ID 550e8400-e29b-41d4-a716-446655440001 not found"
}
```

## Session Management

### Create New Session

Start a new game session for a puzzle with LLM configuration.

**Endpoint:** `POST /api/v1/sessions`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "puzzle_id": "550e8400-e29b-41d4-a716-446655440001",
    "llm_model": "gpt-4",
    "user_id": "user-123"
  }'
```

**Available LLM Models:**
- `gpt-4` - OpenAI GPT-4 (recommended for best accuracy)
- `gpt-3.5-turbo` - OpenAI GPT-3.5 Turbo (faster, lower cost)
- `claude-3-sonnet` - Anthropic Claude 3 Sonnet
- `claude-3-haiku` - Anthropic Claude 3 Haiku (fastest)

**Response (201 Created):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440002",
  "puzzle_id": "550e8400-e29b-41d4-a716-446655440001",
  "start_time": "2025-09-12T14:31:00Z",
  "last_activity": "2025-09-12T14:31:00Z",
  "status": "active",
  "remaining_words": [
    "BASS", "PIANO", "GUITAR", "DRUMS",
    "SALMON", "TUNA", "COD", "TROUT", 
    "YELLOW", "BLUE", "RED", "GREEN",
    "APPLE", "ORANGE", "BANANA", "GRAPE"
  ],
  "incorrect_evaluation_count": 0,
  "solved_groups_count": 0,
  "solved_groups": [],
  "can_request_recommendation": true,
  "pending_recommendation_id": null,
  "llm_model_config": "gpt-4"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid LLM model specified",
  "details": {
    "provided": "gpt-5",
    "allowed": ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "claude-3-haiku"]
  }
}
```

### Get Session State

Retrieve current state of an active game session.

**Endpoint:** `GET /api/v1/sessions/{session_id}`

**Request:**
```bash
curl http://localhost:8000/api/v1/sessions/660e8400-e29b-41d4-a716-446655440002
```

**Response (200 OK) - Active Session:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440002",
  "puzzle_id": "550e8400-e29b-41d4-a716-446655440001",
  "start_time": "2025-09-12T14:31:00Z",
  "last_activity": "2025-09-12T14:35:30Z",
  "status": "active",
  "remaining_words": [
    "SALMON", "TUNA", "COD", "TROUT", 
    "YELLOW", "BLUE", "RED", "GREEN",
    "APPLE", "ORANGE", "BANANA", "GRAPE"
  ],
  "incorrect_evaluation_count": 0,
  "solved_groups_count": 1,
  "solved_groups": [
    {
      "theme": "Musical Instruments",
      "difficulty": "yellow",
      "words": ["BASS", "PIANO", "GUITAR", "DRUMS"]
    }
  ],
  "can_request_recommendation": true,
  "pending_recommendation_id": null,
  "llm_model_config": "gpt-4"
}
```

**Response (200 OK) - Completed Session:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440002",
  "puzzle_id": "550e8400-e29b-41d4-a716-446655440001",
  "start_time": "2025-09-12T14:31:00Z",
  "last_activity": "2025-09-12T14:42:15Z",
  "status": "completed",
  "remaining_words": [],
  "incorrect_evaluation_count": 1,
  "solved_groups_count": 4,
  "solved_groups": [
    {
      "theme": "Musical Instruments",
      "difficulty": "yellow",
      "words": ["BASS", "PIANO", "GUITAR", "DRUMS"]
    },
    {
      "theme": "Types of Fish",
      "difficulty": "green",
      "words": ["SALMON", "TUNA", "COD", "TROUT"]
    },
    {
      "theme": "Colors",
      "difficulty": "blue",
      "words": ["YELLOW", "BLUE", "RED", "GREEN"]
    },
    {
      "theme": "Fruits",
      "difficulty": "purple",
      "words": ["APPLE", "ORANGE", "BANANA", "GRAPE"]
    }
  ],
  "can_request_recommendation": false,
  "pending_recommendation_id": null,
  "llm_model_config": "gpt-4"
}
```

## AI Recommendations

### Request New Recommendation

Generate an AI-powered word grouping suggestion for the current puzzle state.

**Endpoint:** `POST /api/v1/sessions/{session_id}/recommendations`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/sessions/660e8400-e29b-41d4-a716-446655440002/recommendations
```

**Response (201 Created):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "recommended_words": ["SALMON", "TUNA", "COD", "TROUT"],
  "explanation": "These are all types of fish commonly found in both saltwater and freshwater environments. They are frequently served as seafood and are popular in cooking worldwide.",
  "timestamp": "2025-09-12T14:32:15Z",
  "user_evaluation": null,
  "evaluation_timestamp": null,
  "llm_model": "gpt-4",
  "processing_time_ms": 1850
}
```

**Error Response (409 Conflict) - Pending Recommendation:**
```json
{
  "error": "PENDING_RECOMMENDATION",
  "message": "A recommendation is already pending evaluation. Please evaluate recommendation 770e8400-e29b-41d4-a716-446655440003 before requesting a new one.",
  "details": {
    "pending_recommendation_id": "770e8400-e29b-41d4-a716-446655440003"
  }
}
```

**Error Response (400 Bad Request) - Session Complete:**
```json
{
  "error": "SESSION_COMPLETE",
  "message": "Cannot generate recommendations for completed session"
}
```

### Get Current Pending Recommendation

Retrieve the current unevaluated recommendation for a session.

**Endpoint:** `GET /api/v1/sessions/{session_id}/recommendations`

**Request:**
```bash
curl http://localhost:8000/api/v1/sessions/660e8400-e29b-41d4-a716-446655440002/recommendations
```

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "recommended_words": ["SALMON", "TUNA", "COD", "TROUT"],
  "explanation": "These are all types of fish commonly found in both saltwater and freshwater environments. They are frequently served as seafood and are popular in cooking worldwide.",
  "timestamp": "2025-09-12T14:32:15Z",
  "user_evaluation": null,
  "evaluation_timestamp": null,
  "llm_model": "gpt-4",
  "processing_time_ms": 1850
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "NO_PENDING_RECOMMENDATION",
  "message": "No pending recommendation found for this session"
}
```

### Evaluate Recommendation

Provide feedback on an AI recommendation (correct, incorrect, or one-away).

**Endpoint:** `POST /api/v1/sessions/{session_id}/recommendations/{recommendation_id}/evaluate`

**Request - Correct Evaluation:**
```bash
curl -X POST http://localhost:8000/api/v1/sessions/660e8400-e29b-41d4-a716-446655440002/recommendations/770e8400-e29b-41d4-a716-446655440003/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation": "correct"
  }'
```

**Response (200 OK) - Correct Evaluation:**
```json
{
  "recommendation": {
    "id": "770e8400-e29b-41d4-a716-446655440003",
    "recommended_words": ["SALMON", "TUNA", "COD", "TROUT"],
    "explanation": "These are all types of fish commonly found in both saltwater and freshwater environments...",
    "timestamp": "2025-09-12T14:32:15Z",
    "user_evaluation": "correct",
    "evaluation_timestamp": "2025-09-12T14:33:00Z",
    "llm_model": "gpt-4",
    "processing_time_ms": 1850
  },
  "session_status": "active",
  "next_action": "request_next_recommendation",
  "solved_group": {
    "theme": "Types of Fish",
    "difficulty": "green",
    "words": ["SALMON", "TUNA", "COD", "TROUT"]
  }
}
```

**Request - One-Away Evaluation:**
```bash
curl -X POST http://localhost:8000/api/v1/sessions/660e8400-e29b-41d4-a716-446655440002/recommendations/770e8400-e29b-41d4-a716-446655440003/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation": "one_away"
  }'
```

**Response (200 OK) - One-Away Evaluation:**
```json
{
  "recommendation": {
    "id": "770e8400-e29b-41d4-a716-446655440003",
    "recommended_words": ["SALMON", "APPLE", "COD", "YELLOW"],
    "explanation": "These are all natural, organic items commonly found in nature...",
    "timestamp": "2025-09-12T14:32:15Z",
    "user_evaluation": "one_away",
    "evaluation_timestamp": "2025-09-12T14:33:00Z",
    "llm_model": "gpt-4",
    "processing_time_ms": 1850
  },
  "session_status": "active",
  "next_action": "request_next_recommendation",
  "solved_group": null
}
```

**Request - Incorrect Evaluation:**
```bash
curl -X POST http://localhost:8000/api/v1/sessions/660e8400-e29b-41d4-a716-446655440002/recommendations/770e8400-e29b-41d4-a716-446655440003/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation": "incorrect"
  }'
```

**Response (200 OK) - Game Failure (4 Incorrect):**
```json
{
  "recommendation": {
    "id": "770e8400-e29b-41d4-a716-446655440003",
    "recommended_words": ["BASS", "APPLE", "YELLOW", "SALMON"],
    "explanation": "These items might be related through their common usage...",
    "timestamp": "2025-09-12T14:32:15Z",
    "user_evaluation": "incorrect",
    "evaluation_timestamp": "2025-09-12T14:33:00Z",
    "llm_model": "gpt-4",
    "processing_time_ms": 1850
  },
  "session_status": "failed",
  "next_action": "view_history",
  "solved_group": null
}
```

## History & Analytics

### Get Recommendation History

Retrieve complete recommendation history and session summary.

**Endpoint:** `GET /api/v1/sessions/{session_id}/history`

**Request:**
```bash
curl http://localhost:8000/api/v1/sessions/660e8400-e29b-41d4-a716-446655440002/history
```

**Response (200 OK):**
```json
{
  "recommendations": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440003",
      "recommended_words": ["BASS", "PIANO", "GUITAR", "DRUMS"],
      "explanation": "These are all musical instruments commonly used in bands and orchestras...",
      "timestamp": "2025-09-12T14:31:30Z",
      "user_evaluation": "correct",
      "evaluation_timestamp": "2025-09-12T14:31:45Z",
      "llm_model": "gpt-4",
      "processing_time_ms": 1850
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440004",
      "recommended_words": ["SALMON", "APPLE", "COD", "YELLOW"],
      "explanation": "These are all organic, natural items commonly found in nature...",
      "timestamp": "2025-09-12T14:32:00Z",
      "user_evaluation": "one_away",
      "evaluation_timestamp": "2025-09-12T14:32:30Z",
      "llm_model": "gpt-4",
      "processing_time_ms": 1650
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440005",
      "recommended_words": ["SALMON", "TUNA", "COD", "TROUT"],
      "explanation": "Based on previous one-away feedback, these fish words are likely grouped together...",
      "timestamp": "2025-09-12T14:33:00Z",
      "user_evaluation": "correct",
      "evaluation_timestamp": "2025-09-12T14:33:15Z",
      "llm_model": "gpt-4",
      "processing_time_ms": 1200
    }
  ],
  "session_summary": {
    "total_recommendations": 3,
    "correct_evaluations": 2,
    "incorrect_evaluations": 0,
    "one_away_evaluations": 1,
    "session_duration_minutes": 2.25
  }
}
```

## WebSocket Real-time Communication

### WebSocket Connection

Establish a WebSocket connection for real-time AI recommendation streaming.

**Endpoint:** `ws://localhost:8000/ws/sessions/{session_id}/recommendations`

**JavaScript Client Example:**
```javascript
const sessionId = '660e8400-e29b-41d4-a716-446655440002';
const ws = new WebSocket(`ws://localhost:8000/ws/sessions/${sessionId}/recommendations`);

ws.onopen = function(event) {
  console.log('WebSocket connected');
  
  // Request real-time recommendations
  ws.send(JSON.stringify({
    type: 'request_recommendations',
    request_id: 'req-' + Date.now(),
    include_explanations: true,
    max_suggestions: 3
  }));
};

ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'connection_ack':
      console.log('Connection acknowledged');
      console.log('Remaining words:', message.remaining_words);
      break;
      
    case 'processing_status':
      console.log(`Processing: ${message.status} (${message.progress_percent}%)`);
      updateProgressBar(message.progress_percent);
      break;
      
    case 'partial_recommendation':
      console.log('Partial result:', message.recommendation);
      displayPartialResult(message.recommendation);
      break;
      
    case 'recommendations_complete':
      console.log('Final recommendations:', message.recommendations);
      displayFinalRecommendations(message.recommendations);
      break;
      
    case 'error':
      console.error('WebSocket error:', message.error, message.message);
      break;
  }
};

ws.onerror = function(error) {
  console.error('WebSocket error:', error);
};

ws.onclose = function(event) {
  console.log('WebSocket closed:', event.code, event.reason);
};
```

**WebSocket Message Types:**

**Connection Acknowledgment:**
```json
{
  "type": "connection_ack",
  "session_id": "660e8400-e29b-41d4-a716-446655440002",
  "remaining_words": ["YELLOW", "BLUE", "RED", "GREEN", "APPLE", "ORANGE", "BANANA", "GRAPE"],
  "timestamp": "2025-09-12T14:34:00Z"
}
```

**Processing Status Updates:**
```json
{
  "type": "processing_status",
  "request_id": "req-1726150440123",
  "status": "analyzing_word_relationships",
  "progress_percent": 45,
  "timestamp": "2025-09-12T14:34:02Z"
}
```

**Partial Recommendation:**
```json
{
  "type": "partial_recommendation",
  "request_id": "req-1726150440123",
  "recommendation": {
    "confidence": 0.78,
    "words": ["YELLOW", "BLUE", "RED"],
    "partial_explanation": "These are primary colors..."
  },
  "timestamp": "2025-09-12T14:34:03Z"
}
```

**Final Recommendations:**
```json
{
  "type": "recommendations_complete",
  "request_id": "req-1726150440123",
  "recommendations": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440006",
      "recommended_words": ["YELLOW", "BLUE", "RED", "GREEN"],
      "explanation": "These are all primary and secondary colors in the traditional color wheel...",
      "confidence": 0.92,
      "processing_time_ms": 1400
    }
  ],
  "timestamp": "2025-09-12T14:34:04Z"
}
```

## Health Check Endpoints

### Server Health

Check overall server health and status.

**Endpoint:** `GET /health`

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-12T14:35:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

### Database Health

Verify database connectivity and status.

**Endpoint:** `GET /health/db`

**Request:**
```bash
curl http://localhost:8000/health/db
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "response_time_ms": 12,
  "timestamp": "2025-09-12T14:35:00Z"
}
```

### LLM Service Health

Check LLM service connectivity and model availability.

**Endpoint:** `GET /health/llm`

**Request:**
```bash
curl http://localhost:8000/health/llm
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "models": {
    "gpt-4": {
      "available": true,
      "response_time_ms": 850,
      "last_check": "2025-09-12T14:34:45Z"
    },
    "gpt-3.5-turbo": {
      "available": true,
      "response_time_ms": 650,
      "last_check": "2025-09-12T14:34:45Z"
    },
    "claude-3-sonnet": {
      "available": false,
      "error": "API key not configured",
      "last_check": "2025-09-12T14:34:45Z"
    }
  },
  "timestamp": "2025-09-12T14:35:00Z"
}
```

## Error Handling

### Common Error Responses

**Validation Error (400 Bad Request):**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": {
    "field": "llm_model",
    "issue": "must be one of: gpt-4, gpt-3.5-turbo, claude-3-sonnet, claude-3-haiku"
  }
}
```

**Resource Not Found (404 Not Found):**
```json
{
  "error": "NOT_FOUND",
  "message": "Session with ID 660e8400-e29b-41d4-a716-446655440002 not found"
}
```

**Business Logic Error (409 Conflict):**
```json
{
  "error": "PENDING_RECOMMENDATION",
  "message": "A recommendation is already pending evaluation",
  "details": {
    "pending_recommendation_id": "770e8400-e29b-41d4-a716-446655440003",
    "action_required": "evaluate_pending_recommendation"
  }
}
```

**Rate Limiting (429 Too Many Requests):**
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please wait before making another request.",
  "details": {
    "retry_after_seconds": 60,
    "requests_per_minute": 10
  }
}
```

**Internal Server Error (500 Internal Server Error):**
```json
{
  "error": "INTERNAL_ERROR",
  "message": "An unexpected error occurred while processing your request",
  "details": {
    "request_id": "req-1726150440123",
    "timestamp": "2025-09-12T14:35:00Z"
  }
}
```

### LLM Service Errors

**LLM Timeout (503 Service Unavailable):**
```json
{
  "error": "LLM_SERVICE_TIMEOUT",
  "message": "AI recommendation service timed out",
  "details": {
    "timeout_seconds": 30,
    "model": "gpt-4",
    "retry_recommended": true
  }
}
```

**LLM Rate Limit (503 Service Unavailable):**
```json
{
  "error": "LLM_RATE_LIMIT",
  "message": "AI service rate limit exceeded",
  "details": {
    "provider": "openai",
    "retry_after_seconds": 120
  }
}
```

## Performance Guidelines

- **AI Recommendations**: Target response time < 2 seconds
- **API Operations**: Non-AI endpoints should respond < 100ms
- **WebSocket**: Real-time updates within 50ms
- **File Upload**: Support files up to 1MB
- **Concurrent Sessions**: Support 100+ simultaneous users
- **Request Rate Limits**: 10 requests per minute per session for AI endpoints

## SDK Examples

### Python SDK Usage

```python
import requests
import json

class ConnectionsAPIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def upload_puzzle(self, file_path, user_id=None):
        """Upload a puzzle file and create a new puzzle."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'user_id': user_id} if user_id else {}
            response = requests.post(f"{self.base_url}/api/v1/puzzles/upload", 
                                   files=files, data=data)
        return response.json()
    
    def create_session(self, puzzle_id, llm_model="gpt-4", user_id=None):
        """Create a new game session."""
        data = {
            "puzzle_id": puzzle_id,
            "llm_model": llm_model,
            "user_id": user_id
        }
        response = requests.post(f"{self.base_url}/api/v1/sessions", 
                               json=data)
        return response.json()
    
    def get_recommendation(self, session_id):
        """Request a new AI recommendation."""
        response = requests.post(f"{self.base_url}/api/v1/sessions/{session_id}/recommendations")
        return response.json()
    
    def evaluate_recommendation(self, session_id, recommendation_id, evaluation):
        """Evaluate a recommendation (correct/incorrect/one_away)."""
        data = {"evaluation": evaluation}
        response = requests.post(
            f"{self.base_url}/api/v1/sessions/{session_id}/recommendations/{recommendation_id}/evaluate",
            json=data
        )
        return response.json()

# Usage example
client = ConnectionsAPIClient()

# Upload puzzle
puzzle = client.upload_puzzle("my_puzzle.txt", "user-123")

# Create session  
session = client.create_session(puzzle["id"], "gpt-4", "user-123")

# Get recommendation
recommendation = client.get_recommendation(session["id"])

# Evaluate as correct
result = client.evaluate_recommendation(
    session["id"], 
    recommendation["id"], 
    "correct"
)
```

This comprehensive API documentation covers all endpoints with detailed examples for successful integration with the NYT Connections Puzzle Assistant web application.
