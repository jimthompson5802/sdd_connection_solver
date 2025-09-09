# Quickstart Guide: NYT Connections Puzzle Assistant

**Version**: 1.0.0  
**Last Updated**: September 8, 2025  

This guide walks through the complete user workflow for the NYT Connections Puzzle Assistant, providing step-by-step API interactions and expected responses.

## Prerequisites

- Backend server running on `localhost:8000`
- Frontend served from `localhost:3000` (or static files)
- Valid puzzle data loaded in the system

## User Story Walkthrough

### Step 1: Load a New Puzzle
**User Action**: User opens the web application  
**System Action**: Create a new puzzle and session

```bash
# Create a puzzle with 16 words
curl -X POST http://localhost:8000/api/v1/puzzles \
  -H "Content-Type: application/json" \
  -d '{
    "words": ["BASS", "PIANO", "GUITAR", "DRUMS", "SALMON", "TUNA", "COD", "TROUT", "YELLOW", "BLUE", "RED", "GREEN", "APPLE", "ORANGE", "BANANA", "GRAPE"],
    "groups": [
      {
        "theme": "Musical Instruments",
        "difficulty": "yellow", 
        "word_indices": [0, 1, 2, 3]
      },
      {
        "theme": "Types of Fish",
        "difficulty": "green",
        "word_indices": [4, 5, 6, 7] 
      },
      {
        "theme": "Colors",
        "difficulty": "blue",
        "word_indices": [8, 9, 10, 11]
      },
      {
        "theme": "Fruits",
        "difficulty": "purple",
        "word_indices": [12, 13, 14, 15]
      }
    ],
    "difficulty_level": "medium"
  }'
```

**Expected Response**:
```json
{
  "id": "puzzle-uuid-123",
  "words": ["BASS", "PIANO", "GUITAR", "DRUMS", "SALMON", "TUNA", "COD", "TROUT", "YELLOW", "BLUE", "RED", "GREEN", "APPLE", "ORANGE", "BANANA", "GRAPE"],
  "created_at": "2025-09-08T20:00:00Z",
  "difficulty_level": "medium"
}
```

### Step 2: Start a Game Session
**User Action**: Begin solving the puzzle  
**System Action**: Create session and display 16 words

```bash
# Create session for the puzzle
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "puzzle_id": "puzzle-uuid-123"
  }'
```

**Expected Response**:
```json
{
  "id": "session-uuid-456", 
  "puzzle_id": "puzzle-uuid-123",
  "start_time": "2025-09-08T20:01:00Z",
  "last_activity": "2025-09-08T20:01:00Z",
  "status": "active",
  "remaining_words": ["BASS", "PIANO", "GUITAR", "DRUMS", "SALMON", "TUNA", "COD", "TROUT", "YELLOW", "BLUE", "RED", "GREEN", "APPLE", "ORANGE", "BANANA", "GRAPE"],
  "incorrect_guess_count": 0,
  "solved_groups_count": 0,
  "solved_groups": [],
  "can_make_guess": true
}
```

### Step 3: Request AI Recommendations
**User Action**: Click "Get AI Help" button  
**System Action**: Generate word grouping suggestions

```bash
# Request recommendations
curl -X POST http://localhost:8000/api/v1/sessions/session-uuid-456/recommendations
```

**Expected Response** (Async request accepted):
```json
{
  "request_id": "rec-uuid-789",
  "status": "processing",
  "estimated_completion_seconds": 2
}
```

**Fetch recommendations after processing**:
```bash
curl http://localhost:8000/api/v1/sessions/session-uuid-456/recommendations
```

**Expected Response**:
```json
{
  "id": "rec-uuid-789",
  "recommendations": [
    {
      "words": ["BASS", "PIANO", "GUITAR", "DRUMS"],
      "explanation": "These are all musical instruments commonly used in bands and orchestras",
      "confidence": 0.95
    },
    {
      "words": ["SALMON", "TUNA", "COD", "TROUT"], 
      "explanation": "These are all types of fish commonly eaten as food",
      "confidence": 0.88
    },
    {
      "words": ["APPLE", "ORANGE", "BANANA", "GRAPE"],
      "explanation": "These are all common fruits",
      "confidence": 0.82
    }
  ],
  "timestamp": "2025-09-08T20:01:02Z",
  "confidence_scores": {
    "recommendation_0": 0.95,
    "recommendation_1": 0.88, 
    "recommendation_2": 0.82
  },
  "processing_time_ms": 1850,
  "llm_model": "gpt-4"
}
```

### Step 4: Make a Correct Guess
**User Action**: Select "BASS", "PIANO", "GUITAR", "DRUMS" and submit  
**System Action**: Validate guess and update game state

```bash
curl -X POST http://localhost:8000/api/v1/sessions/session-uuid-456/guesses \
  -H "Content-Type: application/json" \
  -d '{
    "selected_words": ["BASS", "PIANO", "GUITAR", "DRUMS"],
    "ai_recommendation_id": "rec-uuid-789"
  }'
```

**Expected Response**:
```json
{
  "id": "guess-uuid-001",
  "selected_words": ["BASS", "PIANO", "GUITAR", "DRUMS"],
  "result": "correct",
  "timestamp": "2025-09-08T20:01:05Z",
  "matched_group": {
    "theme": "Musical Instruments",
    "difficulty": "yellow",
    "words": ["BASS", "PIANO", "GUITAR", "DRUMS"]
  },
  "session_status": "active"
}
```

### Step 5: Verify Updated Session State
**User Action**: UI updates to remove solved words  
**System Action**: Session reflects new state

```bash
curl http://localhost:8000/api/v1/sessions/session-uuid-456
```

**Expected Response**:
```json
{
  "id": "session-uuid-456",
  "puzzle_id": "puzzle-uuid-123", 
  "start_time": "2025-09-08T20:01:00Z",
  "last_activity": "2025-09-08T20:01:05Z",
  "status": "active",
  "remaining_words": ["SALMON", "TUNA", "COD", "TROUT", "YELLOW", "BLUE", "RED", "GREEN", "APPLE", "ORANGE", "BANANA", "GRAPE"],
  "incorrect_guess_count": 0,
  "solved_groups_count": 1,
  "solved_groups": [
    {
      "theme": "Musical Instruments", 
      "difficulty": "yellow",
      "words": ["BASS", "PIANO", "GUITAR", "DRUMS"]
    }
  ],
  "can_make_guess": true
}
```

### Step 6: Make an Incorrect Guess
**User Action**: Select "YELLOW", "APPLE", "SALMON", "PIANO" and submit  
**System Action**: Mark guess as incorrect, increment counter

```bash
curl -X POST http://localhost:8000/api/v1/sessions/session-uuid-456/guesses \
  -H "Content-Type: application/json" \
  -d '{
    "selected_words": ["YELLOW", "APPLE", "SALMON", "PIANO"]
  }'
```

**Expected Response**:
```json
{
  "id": "guess-uuid-002",
  "selected_words": ["YELLOW", "APPLE", "SALMON", "PIANO"],
  "result": "incorrect", 
  "timestamp": "2025-09-08T20:02:00Z",
  "matched_group": null,
  "session_status": "active"
}
```

### Step 7: Make a "One-Away" Guess  
**User Action**: Select "SALMON", "TUNA", "COD", "APPLE" (3 fish + 1 fruit)  
**System Action**: Mark as one-away

```bash
curl -X POST http://localhost:8000/api/v1/sessions/session-uuid-456/guesses \
  -H "Content-Type: application/json" \
  -d '{
    "selected_words": ["SALMON", "TUNA", "COD", "APPLE"]
  }'
```

**Expected Response**:
```json
{
  "id": "guess-uuid-003",
  "selected_words": ["SALMON", "TUNA", "COD", "APPLE"],
  "result": "one_away",
  "timestamp": "2025-09-08T20:02:30Z", 
  "matched_group": null,
  "session_status": "active"
}
```

### Step 8: View Guess History
**User Action**: Check previous attempts  
**System Action**: Return chronological guess list

```bash
curl http://localhost:8000/api/v1/sessions/session-uuid-456/guesses
```

**Expected Response**:
```json
{
  "guesses": [
    {
      "id": "guess-uuid-001",
      "selected_words": ["BASS", "PIANO", "GUITAR", "DRUMS"],
      "result": "correct",
      "timestamp": "2025-09-08T20:01:05Z",
      "matched_group": {
        "theme": "Musical Instruments",
        "difficulty": "yellow", 
        "words": ["BASS", "PIANO", "GUITAR", "DRUMS"]
      }
    },
    {
      "id": "guess-uuid-002", 
      "selected_words": ["YELLOW", "APPLE", "SALMON", "PIANO"],
      "result": "incorrect",
      "timestamp": "2025-09-08T20:02:00Z",
      "matched_group": null
    },
    {
      "id": "guess-uuid-003",
      "selected_words": ["SALMON", "TUNA", "COD", "APPLE"], 
      "result": "one_away",
      "timestamp": "2025-09-08T20:02:30Z",
      "matched_group": null
    }
  ]
}
```

### Step 9: WebSocket Real-time Recommendations
**User Action**: Request new recommendations via WebSocket  
**System Action**: Stream recommendations as they're generated

```javascript
// Frontend WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/sessions/session-uuid-456/recommendations');

ws.onopen = function() {
  // Request recommendations
  ws.send(JSON.stringify({
    type: 'request_recommendations',
    request_id: 'req-uuid-999',
    include_explanations: true,
    max_suggestions: 3
  }));
};

ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  
  // Handle different message types
  switch(message.type) {
    case 'connection_ack':
      console.log('Connected, remaining words:', message.remaining_words);
      break;
      
    case 'processing_status':
      console.log('Status:', message.status, 'Progress:', message.progress_percent + '%');
      break;
      
    case 'partial_recommendation':
      console.log('Partial result:', message.recommendation);
      break;
      
    case 'recommendations_complete':
      console.log('Final recommendations:', message.recommendations);
      break;
  }
};
```

## Testing Validation

### Integration Test Scenarios
1. **Complete Puzzle Success**: User solves all 4 groups correctly
2. **Puzzle Failure**: User makes 4 incorrect guesses  
3. **Mixed Results**: Combination of correct, incorrect, and one-away guesses
4. **AI Recommendation Accuracy**: Verify LLM suggestions match expected patterns
5. **Session Persistence**: Browser refresh maintains game state
6. **Concurrent Sessions**: Multiple users playing different puzzles
7. **Error Handling**: Network failures, invalid inputs, API timeouts

### Performance Validation  
- AI recommendations complete within 2 seconds
- WebSocket connections handle 100+ concurrent users
- API responses under 100ms for non-AI operations
- Frontend UI updates within 50ms of user interaction

### Security Testing
- Session isolation (users can't access other sessions)
- Input sanitization (malformed guess data handled)
- Rate limiting prevents API abuse
- WebSocket connections properly authenticated

## Troubleshooting

### Common Issues
- **AI recommendations timeout**: Check OpenAI API key and rate limits
- **WebSocket connection fails**: Verify session ID and server status
- **Guess validation errors**: Ensure exactly 4 words selected from remaining words
- **Session state inconsistent**: Check database/storage consistency

### Health Check Endpoints
```bash
# Server health
curl http://localhost:8000/health

# Database connectivity  
curl http://localhost:8000/health/db

# LLM API connectivity
curl http://localhost:8000/health/llm
```

This quickstart validates the complete user journey from puzzle creation through game completion, ensuring all functional requirements are met.
