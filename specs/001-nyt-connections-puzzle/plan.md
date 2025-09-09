# Implementation Plan: NYT Connections Puzzle Assistant Web Application

**Branch**: `001-nyt-connections-puzzle` | **Date**: September 8, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-nyt-connections-puzzle/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
A web application that assists users in solving NYT Connections puzzles by providing AI-generated word grouping recommendations, tracking user guesses and progress, and managing puzzle state through a FastAPI backend with HTML/CSS/TypeScript frontend.

## Technical Context
**Language/Version**: Python 3.12+ (backend), HTML/CSS/TypeScript (frontend)  
**Primary Dependencies**: FastAPI, uvicorn, langchain, langgraph, openai, pydantic, requests (backend)  
**Storage**: Session-based storage for puzzle state and guess history  
**Testing**: pytest, pytest-mock (backend), playwright (E2E testing)  
**Target Platform**: Web application (browser-based frontend, server-based backend)
**Project Type**: web (frontend + backend structure)  
**Performance Goals**: AI recommendation requests and UI updates within 2 seconds  
**Constraints**: Exactly 4 incorrect guesses per puzzle, secure data storage  
**Scale/Scope**: Single-user puzzle sessions, 16-word puzzles with 4 groups of 4 words each

**Arguments**: 
- Python 3.12+ backend with HTML/CSS/TypeScript frontend
- Required packages: langchain, langgraph, openai, pydantic, pytest, pytest-mock, requests, fastapi, uvicorn, uv, playwright
- Development environment: VS Code with workspace settings, Git/GitHub, venv virtual environment
- Package management: uv for package management and running scripts
- Linting: flake8, black, isort
- Testing: pytest for backend, playwright for E2E

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 2 (backend + frontend) - within max 3
- Using framework directly? Yes (FastAPI, no wrapper classes)
- Single data model? Yes (puzzle entities mapped to backend models)
- Avoiding patterns? Yes (direct service architecture, no Repository pattern for this scope)

**Architecture**:
- EVERY feature as library? Yes (puzzle logic, AI integration, session management)
- Libraries listed: puzzle-core (game logic), ai-recommendations (LLM integration), session-manager (state tracking)
- CLI per library: --help/--version/--format support planned
- Library docs: llms.txt format planned

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes (tests written first)
- Git commits show tests before implementation? Will be enforced
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes (actual LLM calls, browser testing)
- Integration tests for: new libraries, contract changes, shared schemas? Yes
- FORBIDDEN: Implementation before test, skipping RED phase - ENFORCED

**Observability**:
- Structured logging included? Yes (FastAPI + Python logging)
- Frontend logs → backend? Yes (unified stream planned)
- Error context sufficient? Yes (detailed error responses)

**Versioning**:
- Version number assigned? 1.0.0 (MAJOR.MINOR.BUILD)
- BUILD increments on every change? Yes
- Breaking changes handled? Yes (parallel tests, migration plan)

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 2 (Web application - frontend + backend detected)

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `/scripts/update-agent-context.sh [claude|gemini|copilot]` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Backend API endpoints → FastAPI route implementation tasks [P]
- Data models → Pydantic model creation tasks [P]
- WebSocket handlers → real-time communication tasks
- Frontend components → TypeScript module tasks [P]
- Integration tests → contract validation tasks
- E2E tests → Playwright test scenarios

**Ordering Strategy**:
- TDD order: Tests before implementation (contract tests → integration tests → unit tests → implementation)
- Dependency order: Models → Services → API routes → Frontend components
- Parallel execution: Mark [P] for independent files that can be developed concurrently
- Critical path: AI recommendation system (backend + WebSocket + frontend integration)

**Estimated Output**: 32-38 numbered, ordered tasks in tasks.md covering:
1. Project setup and environment (5 tasks)
2. Backend data models and validation (6 tasks) 
3. Contract tests for all API endpoints (8 tasks)
4. Backend service layer implementation (7 tasks)
5. WebSocket real-time communication (4 tasks)
6. Frontend TypeScript modules (6 tasks)
7. Integration and E2E testing (4 tasks)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS  
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented (N/A - no violations)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*