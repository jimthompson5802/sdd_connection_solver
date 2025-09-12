"""
Storage package for NYT Connections Puzzle Assistant.

This package contains storage implementations for managing game data
including sessions, puzzles, recommendations, and AI contexts.
"""

from .session_storage import (
    BaseStorage,
    InMemoryStorage,
    StorageError,
    SessionNotFoundError,
    PuzzleNotFoundError,
    RecommendationNotFoundError,
    get_storage,
    initialize_storage,
    cleanup_storage,
)

__all__ = [
    "BaseStorage",
    "InMemoryStorage",
    "StorageError",
    "SessionNotFoundError",
    "PuzzleNotFoundError",
    "RecommendationNotFoundError",
    "get_storage",
    "initialize_storage",
    "cleanup_storage",
]
