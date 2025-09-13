"""Service singletons for the backend package.

Expose a single SessionService instance so API routers and tests can share
the same in-memory store. This makes it possible for test fixtures to seed
data deterministically.
"""

from .session_service import SessionService

# Singleton instances exported for application-wide use
session_service = SessionService()

__all__ = ["session_service"]
"""Services package for NYT Connections puzzle application."""

from .puzzle_service import PuzzleService
from .session_service import SessionService
from .llm_service import LLMService
from .evaluation_service import EvaluationService
from .context_service import ContextService

__all__ = ["PuzzleService", "SessionService", "LLMService", "EvaluationService", "ContextService"]
