# Tasks: NYT Connections Puzzle Assistant Web Ap### Contract Tests (API Endpoints)
- [x] T006 [P] Contract test POST /api/v1/puzzles/upload in backend/tests/contract/test_puzzles_upload.py
- [x] T007 [P] Contract test GET /api/v1/puzzles/{puzzle_id} in backend/tests/contract/test_puzzles_get.py
- [x] T008 [P] Contract test POST /api/v1/sessions in backend/tests/contract/test_sessions_create.py
- [ ] T009 [P] Contract test GET /api/v1/sessions/{session_id} in backend/tests/contract/test_sessions_get.pytion

**Input**: Design documents from `/specs/001-nyt-connections-puzzle/`  
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.12+, FastAPI, HTML/CSS/TypeScript
   → Structure: Web application (backend + frontend)
   → Libraries: langchain, langgraph, openai, pydantic, pytest, fastapi, uvicorn
2. Load design documents:
   → data-model.md: Puzzle, Word, Group, Recommendation, Session, AIRecommendationContext entities
   → contracts/api.yaml: 7 REST endpoints + WebSocket connection
   → quickstart.md: Complete user workflow validation scenarios
3. Generate tasks by category:
   → Setup: project structure, dependencies, linting (backend/frontend)
   → Tests: contract tests for all API endpoints, integration tests
   → Core: data models, services, API endpoints, frontend components
   → Integration: LLM integration, WebSocket communication, file upload
   → Polish: unit tests, performance validation, documentation
4. Apply task rules:
   → Contract tests [P] for independent endpoints
   → Model creation [P] for independent entities
   → Frontend components [P] for independent files
   → Sequential for shared files/services
5. TDD enforcement: All tests before implementation
6. Web app structure: backend/ and frontend/ directories
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

## Phase 3.1: Setup
- [x] T001 Create web application project structure (backend/ and frontend/ directories)
- [x] T002 Initialize Python backend with FastAPI dependencies in backend/requirements.txt
- [x] T003 Initialize TypeScript frontend with basic HTML/CSS structure
- [x] T004 [P] Configure Python linting (flake8, black, isort) in backend/.flake8, backend/pyproject.toml
- [x] T005 [P] Configure frontend build and WebSocket client setup in frontend/package.json

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (API Endpoints)
- [x] T006 [P] Contract test POST /api/v1/puzzles/upload in backend/tests/contract/test_puzzles_upload.py
- [x] T007 [P] Contract test GET /api/v1/puzzles/{puzzle_id} in backend/tests/contract/test_puzzles_get.py
- [x] T008 [P] Contract test POST /api/v1/sessions in backend/tests/contract/test_sessions_create.py
- [x] T009 [P] Contract test GET /api/v1/sessions/{session_id} in backend/tests/contract/test_sessions_get.py
- [x] T010 [P] Contract test POST /api/v1/sessions/{session_id}/recommendations in backend/tests/contract/test_recommendations_create.py
- [x] T011 [P] Contract test GET /api/v1/sessions/{session_id}/recommendations in backend/tests/contract/test_recommendations_get.py
- [x] T012 [P] Contract test POST /api/v1/sessions/{session_id}/recommendations/{recommendation_id}/evaluate in backend/tests/contract/test_recommendations_evaluate.py
- [x] T013 [P] Contract test GET /api/v1/sessions/{session_id}/history in backend/tests/contract/test_history.py

### Integration Tests (User Stories)
- [x] T014 [P] Integration test complete puzzle upload workflow in backend/tests/integration/test_puzzle_upload_flow.py
- [x] T015 [P] Integration test session creation with LLM model selection in backend/tests/integration/test_session_creation.py
- [x] T016 [P] Integration test AI recommendation generation with context in backend/tests/integration/test_ai_recommendations.py
- [x] T017 [P] Integration test evaluation workflow (correct/incorrect/one-away) in backend/tests/integration/test_evaluation_flow.py
- [x] T018 [P] Integration test complete game session from upload to completion in backend/tests/integration/test_complete_game.py

### Frontend Integration Tests
- [x] T019 [P] E2E test file upload and puzzle creation in frontend/tests/e2e/test_file_upload.spec.ts
- [x] T020 [P] E2E test recommendation evaluation workflow in frontend/tests/e2e/test_evaluation.spec.ts

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models
- [x] T021 [P] Puzzle model in backend/src/models/puzzle.py
- [x] T022 [P] Word model in backend/src/models/word.py
- [x] T023 [P] Group model in backend/src/models/group.py
- [x] T024 [P] Recommendation model in backend/src/models/recommendation.py
- [x] T025 [P] Session model in backend/src/models/session.py
- [x] T026 [P] AIRecommendationContext model in backend/src/models/ai_context.py
- [x] T027 [P] OneAwayGroup model in backend/src/models/one_away_group.py

### Services Layer
- [x] T028 [P] Puzzle service for file upload and word validation in backend/src/services/puzzle_service.py
- [x] T029 [P] Session service for game state management in backend/src/services/session_service.py
- [x] T030 LLM recommendation service with context-aware prompting in backend/src/services/llm_service.py
- [x] T031 Evaluation service for processing user feedback in backend/src/services/evaluation_service.py
- [x] T032 [P] Context service for managing AI recommendation context in backend/src/services/context_service.py

### API Endpoints
- [ ] T033 [P] POST /api/v1/puzzles/upload endpoint with file handling in backend/src/api/puzzles.py
- [ ] T034 [P] GET /api/v1/puzzles/{puzzle_id} endpoint in backend/src/api/puzzles.py
- [ ] T035 [P] POST /api/v1/sessions endpoint with LLM model config in backend/src/api/sessions.py
- [ ] T036 [P] GET /api/v1/sessions/{session_id} endpoint in backend/src/api/sessions.py
- [ ] T037 POST /api/v1/sessions/{session_id}/recommendations endpoint with LLM integration in backend/src/api/recommendations.py
- [ ] T038 GET /api/v1/sessions/{session_id}/recommendations endpoint in backend/src/api/recommendations.py
- [ ] T039 POST /api/v1/sessions/{session_id}/recommendations/{recommendation_id}/evaluate endpoint in backend/src/api/recommendations.py
- [ ] T040 [P] GET /api/v1/sessions/{session_id}/history endpoint in backend/src/api/history.py

### Frontend Components
- [ ] T041 [P] File upload component with drag-and-drop support in frontend/src/components/FileUpload.ts
- [ ] T042 [P] Puzzle display component showing remaining words in frontend/src/components/PuzzleView.ts
- [ ] T043 [P] Recommendation display component with explanation in frontend/src/components/RecommendationCard.ts
- [ ] T044 [P] Evaluation buttons component (Correct/Incorrect/One-Away) in frontend/src/components/EvaluationButtons.ts
- [ ] T045 [P] Session status component showing progress in frontend/src/components/SessionStatus.ts
- [ ] T046 [P] History view component for past recommendations in frontend/src/components/HistoryView.ts

## Phase 3.4: Integration

### Backend Integration
- [ ] T047 FastAPI application setup with CORS and middleware in backend/src/main.py
- [ ] T048 Error handling middleware and logging configuration in backend/src/middleware/error_handling.py
- [ ] T049 File upload validation and size limits in backend/src/middleware/file_validation.py
- [ ] T050 Session-based storage with in-memory implementation in backend/src/storage/session_storage.py

### WebSocket Integration
- [ ] T051 WebSocket connection handler for real-time recommendations in backend/src/websockets/recommendation_handler.py
- [ ] T052 [P] Frontend WebSocket client for real-time updates in frontend/src/services/WebSocketService.ts

### LLM Integration
- [ ] T053 LangChain integration with configurable models (OpenAI, Claude) in backend/src/llm/model_factory.py
- [ ] T054 Dynamic prompt template system with context injection in backend/src/llm/prompt_templates.py
- [ ] T055 Context-aware recommendation generation with one-away learning in backend/src/llm/recommendation_engine.py

### Frontend Integration
- [ ] T056 Main application component connecting all features in frontend/src/App.ts
- [ ] T057 API service layer for HTTP requests in frontend/src/services/ApiService.ts
- [ ] T058 State management for game session in frontend/src/services/GameState.ts

## Phase 3.5: Polish

### Unit Tests
- [ ] T059 [P] Unit tests for puzzle validation logic in backend/tests/unit/test_puzzle_validation.py
- [ ] T060 [P] Unit tests for LLM prompt generation in backend/tests/unit/test_prompt_generation.py
- [ ] T061 [P] Unit tests for evaluation processing in backend/tests/unit/test_evaluation_logic.py
- [ ] T062 [P] Unit tests for context management in backend/tests/unit/test_context_service.py

### Performance and Validation
- [ ] T063 Performance tests for AI recommendation generation (<2 seconds) in backend/tests/performance/test_recommendation_timing.py
- [ ] T064 WebSocket connection capacity testing (100+ concurrent users) in backend/tests/performance/test_websocket_capacity.py
- [ ] T065 API response time validation (<100ms for non-AI operations) in backend/tests/performance/test_api_response_times.py

### Documentation and Final Setup
- [ ] T066 [P] Create health check endpoints (/health, /health/db, /health/llm) in backend/src/api/health.py
- [ ] T067 [P] Frontend production build configuration in frontend/webpack.config.js
- [ ] T068 [P] Update documentation with API examples in docs/api-examples.md
- [ ] T069 Execute quickstart guide validation scenarios from specs/001-nyt-connections-puzzle/quickstart.md

## Dependencies

### Sequential Dependencies
- Setup (T001-T005) before all other phases
- Tests (T006-T020) before implementation (T021-T058)
- Models (T021-T027) before Services (T028-T032)
- Services (T028-T032) before API Endpoints (T033-T040)
- Core implementation (T021-T046) before Integration (T047-T058)
- Integration (T047-T058) before Polish (T059-T069)

### Specific Dependencies
- T030 (LLM service) blocks T037 (recommendation endpoint), T055 (recommendation engine)
- T031 (evaluation service) blocks T039 (evaluate endpoint)
- T047 (FastAPI setup) blocks all API endpoints (T033-T040)
- T051 (WebSocket handler) blocks T052 (frontend WebSocket client)
- T053 (LangChain integration) blocks T055 (recommendation engine)

## Parallel Execution Examples

### Contract Tests Phase (can run simultaneously)
```bash
Task: "Contract test POST /api/v1/puzzles/upload in backend/tests/contract/test_puzzles_upload.py"
Task: "Contract test GET /api/v1/puzzles/{puzzle_id} in backend/tests/contract/test_puzzles_get.py"
Task: "Contract test POST /api/v1/sessions in backend/tests/contract/test_sessions_create.py"
Task: "Contract test GET /api/v1/sessions/{session_id} in backend/tests/contract/test_sessions_get.py"
```

### Data Models Phase (can run simultaneously)
```bash
Task: "Puzzle model in backend/src/models/puzzle.py"
Task: "Word model in backend/src/models/word.py" 
Task: "Group model in backend/src/models/group.py"
Task: "Recommendation model in backend/src/models/recommendation.py"
```

### Frontend Components Phase (can run simultaneously)
```bash
Task: "File upload component with drag-and-drop support in frontend/src/components/FileUpload.ts"
Task: "Puzzle display component showing remaining words in frontend/src/components/PuzzleView.ts"
Task: "Recommendation display component with explanation in frontend/src/components/RecommendationCard.ts"
Task: "Evaluation buttons component in frontend/src/components/EvaluationButtons.ts"
```

## Task Generation Rules Applied

1. **From Contracts**: Each endpoint in api.yaml → contract test task [P] + implementation task
2. **From Data Model**: Each entity → model creation task [P]
3. **From User Stories**: Each quickstart scenario → integration test [P]
4. **Ordering**: Setup → Tests → Models → Services → Endpoints → Integration → Polish
5. **Parallel Marking**: Different files marked [P], same files sequential

## Validation Checklist
*GATE: Checked before task execution*

- [x] All 8 API contracts have corresponding tests (T006-T013)
- [x] All 7 entities have model tasks (T021-T027)
- [x] All tests come before implementation (T006-T020 before T021+)
- [x] Parallel tasks are truly independent (different files/components)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] WebSocket integration included (T051-T052)
- [x] LLM integration with context-aware learning (T053-T055)
- [x] Complete user workflow from quickstart.md covered (T014-T018, T069)

## Notes

- Total of 69 tasks covering complete web application
- Emphasizes TDD approach with comprehensive test coverage
- Includes real-time WebSocket communication
- Context-aware AI recommendation system with evaluation learning
- Performance validation for <2 second AI responses
- Full frontend-backend integration
- Follows constitutional principles: tests first, single responsibility, proper error handling

This task list is immediately executable with each task specific enough for LLM completion without additional context.
