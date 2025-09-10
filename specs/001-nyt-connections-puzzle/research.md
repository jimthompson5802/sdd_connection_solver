# Research: NYT Connections Puzzle Assistant Web Application

**Date**: September 8, 2025  
**Feature**: 001-nyt-connections-puzzle  

## Research Tasks

### 1. File Upload and Puzzle Initialization

**Decision**: Use multipart/form-data file upload with CSV parsing
**Rationale**: 
- Simple text file format accessible to non-technical users
- Comma-separated values easily parsed and validated
- FastAPI provides excellent file upload handling with size limits
- No need for complex puzzle creation interface

**Alternatives considered**:
- Manual word entry form: More cumbersome for 16 words
- JSON file upload: Less user-friendly format
- Database of pre-created puzzles: Doesn't meet custom puzzle requirement

### 2. LLM Model Configuration

**Decision**: Runtime LLM model selection via session creation parameter
**Rationale**:
- Allows users to choose based on cost/performance preferences
- Easy to add new models without code changes
- Configuration isolated per session for A/B testing
- Environment variable fallback for default model

**Alternatives considered**:
- Global server configuration: Less flexible for users
- Per-request model selection: Too granular, complicates state
- Multiple endpoints per model: Increases API complexity

### 3. Single Recommendation Workflow

**Decision**: Generate and evaluate one recommendation at a time
**Rationale**:
- Simpler user interface - clear focus on current recommendation
- Better LLM context utilization - learns from each evaluation
- Reduced API costs - only generate what's needed
- Natural conversation flow - mimics human puzzle-solving

**Alternatives considered**:
- Multiple simultaneous recommendations: Overwhelming UI, higher costs
- Batch processing: Doesn't leverage user feedback effectively
- User-initiated bulk recommendations: Complex state management

### 4. Evaluation-Based Learning System

**Decision**: Track user evaluations and use as LLM context for future recommendations
**Rationale**:
- One-away feedback provides valuable constraint information
- Incorrect evaluations prevent repeated bad suggestions
- Context improves recommendation quality over session lifetime
- Enables progressive puzzle solving strategy

**Alternatives considered**:
- Stateless recommendations: Misses learning opportunities
- Only track correct/incorrect: Loses valuable one-away information
- Complex ML training: Overkill for session-level learning

### 5. Context-Aware LLM Prompting System

**Decision**: Dynamic prompt generation with evaluation history and one-away constraints
**Rationale**:
- Incorporates previous incorrect/one-away feedback into new recommendations
- Uses structured prompt templates with variable context injection
- Maintains context about remaining words and solved groups
- Enables progressive puzzle-solving strategy

**Alternatives considered**:
- Static prompts: Misses valuable user feedback context
- Complex prompt chaining: Slower and more expensive
- Separate model fine-tuning: Overkill for session-level learning

### 6. Frontend Technology for File Upload and Evaluation Interface

**Decision**: HTML5 file input with vanilla TypeScript for evaluation workflow
**Rationale**:
- Native file upload handling with drag-and-drop support
- Simple evaluation buttons (Correct/Incorrect/One-Away) don't require framework
- Real-time updates via WebSocket without complex state management
- Progressive enhancement approach works across devices

**Alternatives considered**:
- React with file upload library: Adds complexity for simple upload flow
- Vue.js: Overkill for evaluation interface
- Pure HTML forms: Lacks real-time feedback capabilities

### 7. WebSocket Integration for Real-time Updates

**Decision**: WebSocket for recommendation generation status and evaluation results
**Rationale**:
- Real-time progress updates during LLM processing
- Immediate feedback when evaluations are processed
- Bidirectional communication for history requests
- Better user experience than polling

**Alternatives considered**:
- Server-sent events: One-way communication insufficient
- Polling REST endpoints: Poor user experience, higher server load
- Long-polling: More complex than WebSocket for real-time needs

## Technical Decisions Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| File Upload | HTML5 + multipart/form-data | Native support, user-friendly |
| Backend Framework | FastAPI + uvicorn | File upload, WebSocket, async support |
| LLM Integration | langchain + configurable models | Structured prompts, model flexibility |
| Session Storage | In-memory with persistence hooks | Fast access, easy Redis migration |
| Frontend | Vanilla TypeScript + WebSocket | Simple needs, real-time capability |
| Communication | REST + WebSocket | CRUD operations + real-time updates |
| Context Management | Dynamic prompt templates | Learning from user feedback |

## Implementation Patterns

### Recommendation Generation Flow
1. User uploads file → Parse CSV → Create puzzle
2. User creates session with LLM model choice
3. User requests recommendation → Generate context from history
4. LLM processes context → Stream progress via WebSocket
5. User evaluates recommendation → Update context for next round

### Evaluation Learning System
1. Correct evaluation → Remove words from available pool, mark theme as solved
2. Incorrect evaluation → Add word combination to exclusion list
3. One-away evaluation → Track 3-correct-words constraint, exclude combination
4. Next recommendation → Include all constraints in LLM prompt context

### File Processing Pipeline
1. Validate file format (CSV/TXT with 16 comma-separated words)
2. Parse and clean words (trim whitespace, validate uniqueness)
3. Create puzzle entity with uploaded filename tracking
4. Return puzzle ID for session creation

All research tasks completed. No NEEDS CLARIFICATION items remaining.
