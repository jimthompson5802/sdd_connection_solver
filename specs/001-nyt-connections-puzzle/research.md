# Research: NYT Connections Puzzle Assistant Web Application

**Date**: September 8, 2025  
**Feature**: 001-nyt-connections-puzzle  

## Research Tasks

### 1. LLM Integration for Word Grouping Recommendations

**Decision**: Use OpenAI GPT models via langchain/langgraph integration
**Rationale**: 
- langchain provides structured interface for LLM interactions
- langgraph enables complex reasoning workflows for word grouping
- OpenAI GPT models demonstrate strong performance on semantic word relationships
- Established patterns for prompt engineering in puzzle-solving domain

**Alternatives considered**:
- Direct OpenAI API: Less structured, harder to maintain prompts
- Local models (Ollama): Latency issues, lower accuracy for semantic reasoning
- Anthropic Claude: Good performance but less langchain integration

### 2. Frontend-Backend Communication for Real-time Updates

**Decision**: REST API with JSON responses + WebSocket for real-time updates
**Rationale**:
- FastAPI provides excellent WebSocket support alongside REST endpoints
- REST for stateless operations (submit guess, get puzzle)
- WebSocket for real-time AI recommendation streaming
- Simple to test and debug compared to GraphQL

**Alternatives considered**:
- Pure REST: Would require polling for AI recommendation status
- GraphQL: Overkill for simple CRUD operations
- Server-sent events: Less bidirectional than WebSocket

### 3. Session Management and Puzzle State Persistence

**Decision**: In-memory session storage with Redis-like interface (can use in-memory dict for MVP)
**Rationale**:
- Puzzle sessions are temporary (single-session gameplay)
- No need for permanent user accounts or cross-session persistence
- Fast access for real-time guess tracking
- Easy to scale to Redis later if needed

**Alternatives considered**:
- Database persistence: Overkill for temporary puzzle sessions
- Browser localStorage only: Would lose state on server restart
- File-based storage: Slower and unnecessary complexity

### 4. AI Recommendation System Architecture

**Decision**: Async task queue for AI recommendations with result caching
**Rationale**:
- Meets <2 second response requirement through caching
- Async processing prevents UI blocking
- Cache common word patterns to reduce API calls
- Background task can continue even if user disconnects

**Alternatives considered**:
- Synchronous AI calls: Would block UI, fail 2-second requirement
- Pre-computed recommendations: Not feasible for arbitrary puzzle inputs
- Client-side AI: Model size and latency issues

### 5. Frontend Technology Stack

**Decision**: Vanilla TypeScript with modern ES modules, no framework
**Rationale**:
- Simple puzzle interface doesn't require complex state management
- Faster load times and simpler debugging
- Direct DOM manipulation adequate for word selection UI
- Easy WebSocket integration without framework overhead

**Alternatives considered**:
- React: Overkill for simple word selection interface
- Vue: Adds complexity without significant benefit
- Web Components: Good choice but vanilla TS simpler for this scope

### 6. Testing Strategy for AI Components

**Decision**: Mock AI responses for unit tests, real API calls for integration tests
**Rationale**:
- Fast, reliable unit tests with predictable AI responses
- Integration tests validate actual LLM performance
- Contract tests ensure API response schemas match expectations
- Playwright E2E tests validate full user workflow

**Alternatives considered**:
- Only real API calls: Slow tests, API costs, non-deterministic
- Only mocked responses: Would miss actual LLM performance issues
- Separate AI service: Adds architectural complexity

### 7. Error Handling for LLM Failures

**Decision**: Graceful degradation with cached suggestions and user messaging
**Rationale**:
- API failures should not break puzzle functionality
- Show cached/fallback recommendations when AI unavailable
- Clear user messaging about AI status
- Retry logic with exponential backoff

**Alternatives considered**:
- Fail fast on AI errors: Poor user experience
- Silent failures: Users wouldn't understand missing recommendations
- Synchronous retries: Could exceed 2-second response time

## Technical Decisions Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Backend Framework | FastAPI + uvicorn | Async support, WebSocket, auto documentation |
| LLM Integration | langchain + langgraph + OpenAI | Structured LLM workflows, proven performance |
| Frontend | Vanilla TypeScript | Simple UI needs, no framework overhead |
| Session Storage | In-memory (Redis interface) | Temporary sessions, fast access |
| Communication | REST + WebSocket | REST for CRUD, WebSocket for real-time |
| Testing | pytest + playwright + contract tests | TDD workflow, real dependencies |
| Package Management | uv | Fast installs, modern Python packaging |

## Implementation Patterns

### AI Recommendation Flow
1. User requests recommendations → WebSocket connection established
2. Background task: LLM query with puzzle context
3. Stream partial results to frontend as available
4. Cache final results for subsequent requests
5. Handle failures gracefully with fallback suggestions

### Puzzle State Management
1. Immutable puzzle state objects
2. Event-driven state updates (guess submitted, group solved)
3. Session persistence for browser refresh handling
4. Atomic operations for guess counting and validation

### Testing Approach
1. Contract tests → validate API schemas first
2. Integration tests → test LLM integration with real calls
3. Unit tests → individual component logic with mocks
4. E2E tests → full user workflows with Playwright

All research tasks completed. No NEEDS CLARIFICATION items remaining.
