# Quickstart Guide: NYT Connections Puzzle Assistant

**Version**: 1.0.0  
**Last Updated**: September 9, 2025  

This guide walks through the complete user workflow for the NYT Connections Puzzle Assistant, providing step-by-step API interactions and expected responses.

## Prerequisites

- Backend server running on `localhost:8000`
- Frontend served from `localhost:3000` (or static files)
- LLM model configured (e.g., OpenAI GPT-4 or Claude)

## User Story Walkthrough

### Step 1: Upload a Puzzle File
**User Action**: User uploads a text file with 16 comma-separated words  
**System Action**: Create puzzle from uploaded file

```bash
# Create a puzzle by uploading a text file
curl -X POST http://localhost:8000/api/v1/puzzles/upload \
  -F "file=@puzzle_words.txt" \
  -F "user_id=user-123"

# Contents of puzzle_words.txt:
# BASS,PIANO,GUITAR,DRUMS,SALMON,TUNA,COD,TROUT,YELLOW,BLUE,RED,GREEN,APPLE,ORANGE,BANANA,GRAPE
```

**Expected Response**:
```json
{
  "id": "puzzle-uuid-123",
  "words": ["BASS", "PIANO", "GUITAR", "DRUMS", "SALMON", "TUNA", "COD", "TROUT", "YELLOW", "BLUE", "RED", "GREEN", "APPLE", "ORANGE", "BANANA", "GRAPE"],
  "uploaded_filename": "puzzle_words.txt",
  "created_at": "2025-09-09T20:00:00Z",
  "user_id": "user-123"
}
```

### Step 2: Start a Game Session with LLM Configuration
**User Action**: Begin solving the puzzle with chosen LLM model  
**System Action**: Create session with LLM configuration

```bash
# Create session for the puzzle with LLM model choice
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "puzzle_id": "puzzle-uuid-123",
    "llm_model": "gpt-4",
    "user_id": "user-123"
  }'
```

**Expected Response**:
```json
{
  "id": "session-uuid-456", 
  "puzzle_id": "puzzle-uuid-123",
  "start_time": "2025-09-09T20:01:00Z",
  "last_activity": "2025-09-09T20:01:00Z",
  "status": "active",
  "remaining_words": ["BASS", "PIANO", "GUITAR", "DRUMS", "SALMON", "TUNA", "COD", "TROUT", "YELLOW", "BLUE", "RED", "GREEN", "APPLE", "ORANGE", "BANANA", "GRAPE"],
  "incorrect_evaluation_count": 0,
  "solved_groups_count": 0,
  "solved_groups": [],
  "can_request_recommendation": true,
  "pending_recommendation_id": null,
  "llm_model_config": "gpt-4"
}
```

### Step 3: Request First AI Recommendation
**User Action**: Click "Get AI Recommendation" button  
**System Action**: Generate single word grouping suggestion

```bash
# Request first recommendation
curl -X POST http://localhost:8000/api/v1/sessions/session-uuid-456/recommendations
```

**Expected Response**:
```json
{
  "id": "rec-uuid-001",
  "recommended_words": ["BASS", "PIANO", "GUITAR", "DRUMS"],
  "explanation": "These are all musical instruments commonly used in bands and orchestras. They represent different categories: BASS (string/low frequency), PIANO (keyboard), GUITAR (string), and DRUMS (percussion).",
  "timestamp": "2025-09-09T20:01:02Z",
  "user_evaluation": null,
  "evaluation_timestamp": null,
  "llm_model": "gpt-4",
  "processing_time_ms": 1850
}
```

### Step 4: Evaluate Recommendation as Correct
**User Action**: User indicates the recommendation is correct  
**System Action**: Mark group as solved and update game state

```bash
curl -X POST http://localhost:8000/api/v1/sessions/session-uuid-456/recommendations/rec-uuid-001/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation": "correct"
  }'
```

**Expected Response**:
```json
{
  "recommendation": {
    "id": "rec-uuid-001",
    "recommended_words": ["BASS", "PIANO", "GUITAR", "DRUMS"],
    "explanation": "These are all musical instruments commonly used in bands and orchestras...",
    "user_evaluation": "correct",
    "evaluation_timestamp": "2025-09-09T20:01:05Z",
    "llm_model": "gpt-4",
    "processing_time_ms": 1850
  },
  "session_status": "active",
  "next_action": "request_next_recommendation",
  "solved_group": {
    "theme": "Musical Instruments",
    "difficulty": "yellow",
    "words": ["BASS", "PIANO", "GUITAR", "DRUMS"]
  }
}
```

### Step 5: Verify Updated Session State
**User Action**: UI updates to show progress  
**System Action**: Session reflects new state with remaining words

```bash
curl http://localhost:8000/api/v1/sessions/session-uuid-456
```

**Expected Response**:
```json
{
  "id": "session-uuid-456",
  "puzzle_id": "puzzle-uuid-123", 
  "start_time": "2025-09-09T20:01:00Z",
  "last_activity": "2025-09-09T20:01:05Z",
  "status": "active",
  "remaining_words": ["SALMON", "TUNA", "COD", "TROUT", "YELLOW", "BLUE", "RED", "GREEN", "APPLE", "ORANGE", "BANANA", "GRAPE"],
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

### Step 6: Request Second Recommendation
**User Action**: Request next AI suggestion  
**System Action**: Generate recommendation based on remaining words and context

```bash
curl -X POST http://localhost:8000/api/v1/sessions/session-uuid-456/recommendations
```

**Expected Response**:
```json
{
  "id": "rec-uuid-002",
  "recommended_words": ["SALMON", "APPLE", "COD", "YELLOW"],
  "explanation": "These are all organic, natural items that can be found in nature and are commonly consumed or used by humans.",
  "timestamp": "2025-09-09T20:02:00Z",
  "user_evaluation": null,
  "evaluation_timestamp": null,
  "llm_model": "gpt-4",
  "processing_time_ms": 1650
}
```

### Step 7: Evaluate Recommendation as One-Away
**User Action**: User indicates 3 out of 4 words are correct but doesn't specify which ones  
**System Action**: Track one-away information for future recommendations

```bash
curl -X POST http://localhost:8000/api/v1/sessions/session-uuid-456/recommendations/rec-uuid-002/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation": "one_away"
  }'
```

**Expected Response**:
```json
{
  "recommendation": {
    "id": "rec-uuid-002",
    "recommended_words": ["SALMON", "APPLE", "COD", "YELLOW"],
    "explanation": "These are all organic, natural items...",
    "user_evaluation": "one_away",
    "evaluation_timestamp": "2025-09-09T20:02:30Z",
    "llm_model": "gpt-4",
    "processing_time_ms": 1650
  },
  "session_status": "active",
  "next_action": "request_next_recommendation",
  "solved_group": null
}
```

### Step 8: Request Third Recommendation with Context
**User Action**: Request next recommendation  
**System Action**: Use one-away context to generate better suggestion (knowing 3 of previous 4 words belong together)

```bash
curl -X POST http://localhost:8000/api/v1/sessions/session-uuid-456/recommendations
```

**Expected Response**:
```json
{
  "id": "rec-uuid-003",
  "recommended_words": ["SALMON", "TUNA", "COD", "TROUT"],
  "explanation": "These are all types of fish commonly eaten as seafood. Based on previous one-away feedback, these fish words are likely grouped together rather than with other items.",
  "timestamp": "2025-09-09T20:03:00Z",
  "user_evaluation": null,
  "evaluation_timestamp": null,
  "llm_model": "gpt-4",
  "processing_time_ms": 1200
}
```

### Step 9: View Complete Recommendation History
**User Action**: Check all previous recommendations and evaluations  
**System Action**: Return chronological history with summary

```bash
curl http://localhost:8000/api/v1/sessions/session-uuid-456/history
```

**Expected Response**:
```json
{
  "recommendations": [
    {
      "id": "rec-uuid-001",
      "recommended_words": ["BASS", "PIANO", "GUITAR", "DRUMS"],
      "explanation": "These are all musical instruments...",
      "user_evaluation": "correct",
      "evaluation_timestamp": "2025-09-09T20:01:05Z",
      "llm_model": "gpt-4",
      "processing_time_ms": 1850
    },
    {
      "id": "rec-uuid-002", 
      "recommended_words": ["SALMON", "APPLE", "COD", "YELLOW"],
      "explanation": "These are all organic, natural items...",
      "user_evaluation": "one_away",
      "evaluation_timestamp": "2025-09-09T20:02:30Z",
      "llm_model": "gpt-4",
      "processing_time_ms": 1650
    },
    {
      "id": "rec-uuid-003",
      "recommended_words": ["SALMON", "TUNA", "COD", "TROUT"],
      "explanation": "These are all types of fish...",
      "user_evaluation": null,
      "evaluation_timestamp": null,
      "llm_model": "gpt-4",
      "processing_time_ms": 1200
    }
  ],
  "session_summary": {
    "total_recommendations": 3,
    "correct_evaluations": 1,
    "incorrect_evaluations": 0,
    "one_away_evaluations": 1,
    "session_duration_minutes": 2.0
  }
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
