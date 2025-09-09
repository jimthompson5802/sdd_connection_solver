# WebSocket API Contract: Real-time AI Recommendations

**Endpoint**: `/ws/sessions/{session_id}/recommendations`  
**Protocol**: WebSocket  
**Purpose**: Real-time streaming of AI recommendation generation

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

### Request AI Recommendations
```json
{
  "type": "request_recommendations",
  "request_id": "uuid-string",
  "include_explanations": true,
  "max_suggestions": 4
}
```

**Validation**:
- `request_id` must be unique UUID
- `include_explanations` defaults to true
- `max_suggestions` must be 1-4, defaults to 4

### Cancel Request
```json
{
  "type": "cancel_request", 
  "request_id": "uuid-string"
}
```

## Server → Client Messages

### Connection Acknowledged
```json
{
  "type": "connection_ack",
  "session_id": "uuid-string",
  "remaining_words": ["WORD1", "WORD2", ...],
  "can_request": true
}
```

### Request Acknowledged
```json
{
  "type": "request_ack",
  "request_id": "uuid-string",
  "estimated_completion_ms": 2000
}
```

### Processing Status
```json
{
  "type": "processing_status",
  "request_id": "uuid-string",
  "status": "analyzing_words",
  "progress_percent": 25
}
```

**Status Values**:
- `analyzing_words` - LLM analyzing word relationships
- `generating_groups` - Creating potential groupings
- `calculating_confidence` - Computing confidence scores
- `finalizing` - Preparing final response

### Partial Recommendation
```json
{
  "type": "partial_recommendation",
  "request_id": "uuid-string",
  "recommendation": {
    "words": ["WORD1", "WORD2", "WORD3", "WORD4"],
    "explanation": "These are all types of...",
    "confidence": 0.85
  },
  "sequence_number": 1
}
```

### Complete Recommendations
```json
{
  "type": "recommendations_complete",
  "request_id": "uuid-string",
  "recommendations": [
    {
      "words": ["WORD1", "WORD2", "WORD3", "WORD4"],
      "explanation": "These are all types of fish",
      "confidence": 0.92
    },
    {
      "words": ["WORD5", "WORD6", "WORD7", "WORD8"], 
      "explanation": "These are all musical instruments",
      "confidence": 0.78
    }
  ],
  "processing_time_ms": 1850,
  "llm_model": "gpt-4",
  "confidence_scores": {
    "overall": 0.85,
    "recommendation_0": 0.92,
    "recommendation_1": 0.78
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
