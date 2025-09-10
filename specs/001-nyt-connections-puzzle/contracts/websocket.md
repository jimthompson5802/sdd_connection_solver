# WebSocket API Contract: Real-time AI Recommendations

**Endpoint**: `/ws/sessions/{session_id}/recommendations`  
**Protocol**: WebSocket  
**Purpose**: Real-time streaming of AI recommendation generation and evaluation updates

## Connection Lifecycle

### 1. Connection Establishment
```
Client → Server: WebSocket upgrade request
Headers:
  - Upgrade: websocket
  - Connection: Upgrade
  - Sec-WebSocket-Key: [key]
  - Sec-WebSocket-Version: 13

Server → Client: HTTP 101 Switching Protocols (success)
  OR HTTP 400/404 (failure)
```

### 2. Message Protocol
All messages are JSON format with `type` field for message discrimination.

## Client → Server Messages

### Request AI Recommendation
```json
{
  "type": "generate_recommendation",
  "request_id": "uuid-string"
}
```

**Validation**:
- `request_id` must be unique UUID
- Session must be active and not have pending recommendation
- Must have remaining words to recommend

### Evaluate Current Recommendation
```json
{
  "type": "evaluate_recommendation",
  "recommendation_id": "uuid-string", 
  "evaluation": "correct",
  "one_away_details": {
    "likely_correct_words": ["WORD1", "WORD2", "WORD3"],
    "likely_incorrect_word": "WORD4"
  }
}
```

**Validation**:
- `evaluation` must be "correct", "incorrect", or "one_away"  
- `one_away_details` required only if evaluation is "one_away"
- `recommendation_id` must match current pending recommendation

### Request Session History
```json
{
  "type": "request_history",
  "request_id": "uuid-string"
}
```

## Server → Client Messages

### Connection Acknowledged
```json
{
  "type": "connection_ack",
  "session_id": "uuid-string",
  "session_status": "active",
  "remaining_words": ["WORD1", "WORD2", ...],
  "solved_groups_count": 1,
  "incorrect_evaluation_count": 0,
  "pending_recommendation_id": "uuid-string"
}
```

### Recommendation Generation Status
```json
{
  "type": "generation_status",
  "request_id": "uuid-string",
  "status": "analyzing_words",
  "progress_percent": 25,
  "estimated_completion_ms": 1500
}
```

**Status Values**:
- `analyzing_context` - Processing previous recommendations and evaluations
- `analyzing_words` - LLM analyzing remaining word relationships
- `generating_explanation` - Creating reasoning for grouping
- `finalizing` - Preparing final response

### Recommendation Generated
```json
{
  "type": "recommendation_generated",
  "request_id": "uuid-string",
  "recommendation": {
    "id": "rec-uuid-123",
    "recommended_words": ["WORD1", "WORD2", "WORD3", "WORD4"],
    "explanation": "These are all types of fish commonly eaten as food",
    "timestamp": "2025-09-09T20:00:00Z",
    "llm_model": "gpt-4",
    "processing_time_ms": 1850
  }
}
```

### Evaluation Processed
```json
{
  "type": "evaluation_processed",
  "recommendation": {
    "id": "rec-uuid-123",
    "recommended_words": ["WORD1", "WORD2", "WORD3", "WORD4"],
    "explanation": "These are all types of fish",
    "user_evaluation": "correct",
    "evaluation_timestamp": "2025-09-09T20:01:00Z"
  },
  "session_update": {
    "status": "active",
    "remaining_words": ["WORD5", "WORD6", ...],
    "solved_groups_count": 2,
    "incorrect_evaluation_count": 0
  },
  "solved_group": {
    "theme": "Types of Fish", 
    "difficulty": "green",
    "words": ["WORD1", "WORD2", "WORD3", "WORD4"]
  },
  "next_action": "request_next_recommendation"
}
```

### Session History
```json
{
  "type": "session_history",
  "request_id": "uuid-string",
  "recommendations": [
    {
      "id": "rec-uuid-001",
      "recommended_words": ["BASS", "PIANO", "GUITAR", "DRUMS"],
      "explanation": "These are all musical instruments",
      "user_evaluation": "correct",
      "evaluation_timestamp": "2025-09-09T20:00:00Z"
    },
    {
      "id": "rec-uuid-002", 
      "recommended_words": ["SALMON", "APPLE", "COD", "TROUT"],
      "explanation": "These are all organic items",
      "user_evaluation": "one_away",
      "evaluation_timestamp": "2025-09-09T20:01:00Z"
    }
  ],
  "session_summary": {
    "total_recommendations": 2,
    "correct_evaluations": 1,
    "incorrect_evaluations": 0,
    "one_away_evaluations": 1,
    "session_duration_minutes": 3.5
  }
}
```

### Error Message
```json
{
  "type": "error",
  "request_id": "uuid-string", 
  "error_code": "LLM_API_ERROR",
  "message": "OpenAI API temporarily unavailable",
  "retry_after_ms": 5000
}
```

**Error Codes**:
- `INVALID_SESSION` - Session not found or invalid
- `SESSION_COMPLETED` - Game already finished
- `TOO_MANY_REQUESTS` - Rate limit exceeded  
- `LLM_API_ERROR` - External API failure
- `INTERNAL_ERROR` - Server error

### Session Update
```json
{
  "type": "session_update",
  "session_id": "uuid-string",
  "remaining_words": ["WORD9", "WORD10", ...],
  "solved_groups_count": 2,
  "incorrect_guess_count": 1
}
```

## Connection Management

### Heartbeat/Keepalive
```json
// Client → Server (every 30 seconds)
{
  "type": "ping",
  "timestamp": "2025-09-08T20:00:00Z"
}

// Server → Client  
{
  "type": "pong",
  "timestamp": "2025-09-08T20:00:00Z"
}
```

### Connection Close
**Client Initiated**:
- WebSocket close frame with code 1000 (normal closure)

**Server Initiated**:
- Code 1000: Normal closure
- Code 1003: Invalid message format 
- Code 1008: Policy violation (rate limiting)
- Code 1011: Server error

## Rate Limiting

- Maximum 1 recommendation request per 5 seconds per session
- Maximum 10 concurrent WebSocket connections per IP
- Connection automatically closed after 30 minutes of inactivity

## Error Handling

### Client Responsibilities
1. Handle connection drops gracefully
2. Implement exponential backoff for reconnection
3. Validate server message formats
4. Respect rate limiting

### Server Responsibilities  
1. Validate all incoming messages
2. Handle LLM API failures gracefully
3. Provide meaningful error messages
4. Clean up resources on disconnect

## Message Ordering

- Messages for same `request_id` are delivered in order
- Multiple concurrent requests may interleave messages
- Use `sequence_number` in partial recommendations to ensure ordering

## Security Considerations

- Session ID validation on connection
- Message size limits (max 64KB per message)
- Request rate limiting per session
- Input sanitization for all message fields
