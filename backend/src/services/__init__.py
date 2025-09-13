"""Services package for the backend.

This module creates and exports singleton service instances used across the
application so routers and tests share the same in-memory state.
"""

from .puzzle_service import PuzzleService
from .session_service import SessionService
from .llm_service import LLMService
from .evaluation_service import EvaluationService
from .context_service import ContextService

# Singleton instances exported for application-wide use
puzzle_service = PuzzleService()
session_service = SessionService()
llm_service = LLMService()
evaluation_service = EvaluationService()
context_service = ContextService()

__all__ = [
    "puzzle_service",
    "session_service",
    "llm_service",
    "evaluation_service",
    "context_service",
    "PuzzleService",
    "SessionService",
    "LLMService",
    "EvaluationService",
    "ContextService",
]
