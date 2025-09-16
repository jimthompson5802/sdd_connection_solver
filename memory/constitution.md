## NYT Connections Puzzle Assistant - Project Constitution

## Core Principles

### I. Library-First, Service-Oriented
All functionality should be organized as small, well-scoped modules or services. The backend exposes clear service boundaries (puzzle service, session service, LLM service, evaluation service) and models; the frontend is a discrete TypeScript application that communicates via HTTP and WebSocket. Each module must be independently testable and documented.

### II. API Contracts & Observability
APIs are first-class: routers in `backend/src/api` define explicit JSON contracts and error shapes used by tests. Handlers must return structured error payloads (see `RequestValidationError` -> `VALIDATION_ERROR`) and use consistent status codes to satisfy integration tests. Logging is required for all request/response flows (see `main.py` logging and middleware).

### III. Test-First and Contract Tests
Automated tests are required. The repo contains unit and integration-style tests that rely on deterministic behavior (seeded sessions, mock LLM responses). New features must include tests that assert API contracts and service behavior. Maintain compatibility with existing contract tests.

### IV. Simplicity and In-Memory Defaults
Start simple: services default to in-memory stores (see `PuzzleService`, `SessionService`) and mocked LLM responses for development. Production integrations (persistent storage, real LLM APIs) should be added behind configuration flags and documented migration steps.

### V. Security & Validation
Input validation is enforced at model and router boundaries (Pydantic validators in `models/`). Reject invalid data early with clear, machine-readable errors. CORS and Trusted Host middleware must be configured for allowed origins and hosts.

## Technology & Architecture Constraints

- **Backend**: Python 3.12+, FastAPI, Pydantic v2, Uvicorn. Services organized under `backend/src/services`, API routers under `backend/src/api`, models under `backend/src/models`.
- **Frontend**: TypeScript, Webpack, Playwright for E2E tests. Frontend builds to `dist/` and communicates via REST and WebSocket endpoints (`/api/v1/...`, `/ws/sessions/{session_id}/recommendations`).
- **Testing**: `pytest` for backend, `jest`/`playwright` for frontend. CI must run contract tests that assert API behavior.
- **LLM Integration**: Abstracted behind `LLMService`; mock mode enabled by default for development. Real provider integrations (OpenAI, Anthropic, etc.) must be pluggable and optionally configured via environment variables.


## Development Workflow & Quality Gates

- **Formatting & Linting**: Use `black`, `isort`, `flake8` for Python; `eslint` and `prettier` for frontend. Keep line length ≤ 120 for Python.
- **Type Safety**: Pydantic models for backend; TypeScript strict mode for frontend. Include type annotations on all new Python functions.
- **CI Gates**: PRs must pass unit tests and contract tests, and must not break API shapes used by consumers. New endpoints require OpenAPI docs updates where applicable.
- **Seeded Determinism**: Keep deterministic seeds used by contract tests (see seeded session IDs in `main.py`) to avoid breaking test expectations.

## Governance

- Amendments to this constitution require a short rationale, a migration plan for affected tests, and a code change with updated tests.
- Breaking changes to API contracts require a major-version bump and explicit migration notes in `CHANGELOG.md`.

**Version**: 1.0.0 | **Ratified**: 2025-09-15 | **Last Amended**: 2025-09-15