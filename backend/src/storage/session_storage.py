"""
Session-based storage with in-memory implementation for NYT Connections Puzzle Assistant.

This module provides a comprehensive in-memory storage system for managing
game sessions, puzzles, recommendations, and related data with thread-safe
operations and optional persistence capabilities.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set

from ..models.session import Session
from ..models.puzzle import Puzzle
from ..models.recommendation import Recommendation
from ..models.ai_context import AIRecommendationContext


logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Base exception for storage operations."""

    pass


class SessionNotFoundError(StorageError):
    """Exception raised when session is not found."""

    pass


class PuzzleNotFoundError(StorageError):
    """Exception raised when puzzle is not found."""

    pass


class RecommendationNotFoundError(StorageError):
    """Exception raised when recommendation is not found."""

    pass


class BaseStorage(ABC):
    """Abstract base class for storage implementations."""

    @abstractmethod
    async def create_session(self, session: Session) -> Session:
        """Create a new session."""
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        pass

    @abstractmethod
    async def update_session(self, session: Session) -> Session:
        """Update existing session."""
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete session by ID."""
        pass

    @abstractmethod
    async def create_puzzle(self, puzzle: Puzzle) -> Puzzle:
        """Create a new puzzle."""
        pass

    @abstractmethod
    async def get_puzzle(self, puzzle_id: str) -> Optional[Puzzle]:
        """Get puzzle by ID."""
        pass

    @abstractmethod
    async def create_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Create a new recommendation."""
        pass

    @abstractmethod
    async def get_recommendation(self, recommendation_id: str) -> Optional[Recommendation]:
        """Get recommendation by ID."""
        pass

    @abstractmethod
    async def get_session_recommendations(self, session_id: str) -> List[Recommendation]:
        """Get all recommendations for a session."""
        pass

    @abstractmethod
    async def update_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Update existing recommendation."""
        pass


class InMemoryStorage(BaseStorage):
    """
    Thread-safe in-memory storage implementation.

    Features:
    - Thread-safe operations using asyncio locks
    - Automatic session cleanup based on TTL
    - Data persistence to JSON files (optional)
    - Memory usage monitoring
    - Session indexing for fast lookups
    """

    def __init__(
        self,
        session_ttl_hours: int = 24,
        enable_persistence: bool = False,
        persistence_file: Optional[str] = None,
        cleanup_interval_minutes: int = 60,
        max_sessions: int = 1000,
    ):
        """
        Initialize in-memory storage.

        Args:
            session_ttl_hours: Session time-to-live in hours
            enable_persistence: Enable data persistence to disk
            persistence_file: File path for persistence
            cleanup_interval_minutes: Cleanup interval in minutes
            max_sessions: Maximum number of sessions to keep
        """
        self.session_ttl = timedelta(hours=session_ttl_hours)
        self.enable_persistence = enable_persistence
        self.persistence_file = persistence_file or "storage_data.json"
        self.cleanup_interval = timedelta(minutes=cleanup_interval_minutes)
        self.max_sessions = max_sessions

        # Thread-safe storage containers
        self._sessions: Dict[str, Session] = {}
        self._puzzles: Dict[str, Puzzle] = {}
        self._recommendations: Dict[str, Recommendation] = {}
        self._ai_contexts: Dict[str, AIRecommendationContext] = {}

        # Indexing for performance
        self._session_by_puzzle: Dict[str, Set[str]] = defaultdict(set)
        self._recommendations_by_session: Dict[str, List[str]] = defaultdict(list)
        self._session_access_times: Dict[str, datetime] = {}

        # Locks for thread safety
        self._session_lock = asyncio.Lock()
        self._puzzle_lock = asyncio.Lock()
        self._recommendation_lock = asyncio.Lock()
        self._cleanup_lock = asyncio.Lock()

        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

        # Load persisted data if enabled
        if self.enable_persistence:
            self._load_from_persistence()

    async def start(self) -> None:
        """Start the storage system and background tasks."""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("In-memory storage started")

    async def stop(self) -> None:
        """Stop the storage system and save data if persistence is enabled."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        if self.enable_persistence:
            await self._save_to_persistence()

        logger.info("In-memory storage stopped")

    # Session operations

    async def create_session(self, session: Session) -> Session:
        """Create a new session."""
        async with self._session_lock:
            if session.id in self._sessions:
                raise StorageError(f"Session {session.id} already exists")

            # Check session limit
            if len(self._sessions) >= self.max_sessions:
                await self._cleanup_old_sessions()

            self._sessions[session.id] = session
            self._session_access_times[session.id] = datetime.now()
            self._session_by_puzzle[session.puzzle_id].add(session.id)

            logger.info(f"Created session {session.id}")
            return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        async with self._session_lock:
            session = self._sessions.get(session_id)
            if session:
                self._session_access_times[session_id] = datetime.now()
            return session

    async def update_session(self, session: Session) -> Session:
        """Update existing session."""
        async with self._session_lock:
            if session.id not in self._sessions:
                raise SessionNotFoundError(f"Session {session.id} not found")

            # Update last activity
            session.last_activity = datetime.now()
            self._sessions[session.id] = session
            self._session_access_times[session.id] = datetime.now()

            logger.debug(f"Updated session {session.id}")
            return session

    async def delete_session(self, session_id: str) -> bool:
        """Delete session by ID."""
        async with self._session_lock:
            session = self._sessions.pop(session_id, None)
            if not session:
                return False

            # Clean up related data
            self._session_access_times.pop(session_id, None)
            self._session_by_puzzle[session.puzzle_id].discard(session_id)

            # Remove session recommendations
            recommendation_ids = self._recommendations_by_session.pop(session_id, [])
            async with self._recommendation_lock:
                for rec_id in recommendation_ids:
                    self._recommendations.pop(rec_id, None)

            logger.info(f"Deleted session {session_id}")
            return True

    async def list_sessions(
        self,
        puzzle_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Session]:
        """List sessions with optional filtering."""
        async with self._session_lock:
            sessions = list(self._sessions.values())

            # Apply filters
            if puzzle_id:
                sessions = [s for s in sessions if s.puzzle_id == puzzle_id]
            if status:
                sessions = [s for s in sessions if s.status == status]

            # Sort by last activity (most recent first)
            sessions.sort(key=lambda s: s.last_activity, reverse=True)

            # Apply limit
            if limit:
                sessions = sessions[:limit]

            return sessions

    # Puzzle operations

    async def create_puzzle(self, puzzle: Puzzle) -> Puzzle:
        """Create a new puzzle."""
        async with self._puzzle_lock:
            if puzzle.id in self._puzzles:
                raise StorageError(f"Puzzle {puzzle.id} already exists")

            self._puzzles[puzzle.id] = puzzle
            logger.info(f"Created puzzle {puzzle.id}")
            return puzzle

    async def get_puzzle(self, puzzle_id: str) -> Optional[Puzzle]:
        """Get puzzle by ID."""
        async with self._puzzle_lock:
            return self._puzzles.get(puzzle_id)

    async def list_puzzles(self, limit: Optional[int] = None) -> List[Puzzle]:
        """List puzzles."""
        async with self._puzzle_lock:
            puzzles = list(self._puzzles.values())
            puzzles.sort(key=lambda p: p.created_at, reverse=True)

            if limit:
                puzzles = puzzles[:limit]

            return puzzles

    # Recommendation operations

    async def create_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Create a new recommendation."""
        async with self._recommendation_lock:
            if recommendation.id in self._recommendations:
                raise StorageError(f"Recommendation {recommendation.id} already exists")

            self._recommendations[recommendation.id] = recommendation
            self._recommendations_by_session[recommendation.session_id].append(recommendation.id)

            logger.debug(f"Created recommendation {recommendation.id}")
            return recommendation

    async def get_recommendation(self, recommendation_id: str) -> Optional[Recommendation]:
        """Get recommendation by ID."""
        async with self._recommendation_lock:
            return self._recommendations.get(recommendation_id)

    async def get_session_recommendations(self, session_id: str) -> List[Recommendation]:
        """Get all recommendations for a session."""
        async with self._recommendation_lock:
            recommendation_ids = self._recommendations_by_session.get(session_id, [])
            recommendations = []

            for rec_id in recommendation_ids:
                recommendation = self._recommendations.get(rec_id)
                if recommendation:
                    recommendations.append(recommendation)

            # Sort by timestamp (most recent first)
            recommendations.sort(key=lambda r: r.timestamp, reverse=True)
            return recommendations

    async def update_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Update existing recommendation."""
        async with self._recommendation_lock:
            if recommendation.id not in self._recommendations:
                raise RecommendationNotFoundError(f"Recommendation {recommendation.id} not found")

            self._recommendations[recommendation.id] = recommendation
            logger.debug(f"Updated recommendation {recommendation.id}")
            return recommendation

    # AI Context operations

    async def create_ai_context(self, context: AIRecommendationContext) -> AIRecommendationContext:
        """Create AI recommendation context."""
        self._ai_contexts[context.session_id] = context
        return context

    async def get_ai_context(self, session_id: str) -> Optional[AIRecommendationContext]:
        """Get AI context for session."""
        return self._ai_contexts.get(session_id)

    async def update_ai_context(self, context: AIRecommendationContext) -> AIRecommendationContext:
        """Update AI recommendation context."""
        self._ai_contexts[context.session_id] = context
        return context

    # Statistics and monitoring

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        async with self._session_lock:
            async with self._puzzle_lock:
                async with self._recommendation_lock:
                    active_sessions = sum(1 for s in self._sessions.values() if s.status == "active")

                    return {
                        "sessions": {
                            "total": len(self._sessions),
                            "active": active_sessions,
                            "completed": sum(1 for s in self._sessions.values() if s.status == "completed"),
                        },
                        "puzzles": {"total": len(self._puzzles)},
                        "recommendations": {"total": len(self._recommendations)},
                        "ai_contexts": {"total": len(self._ai_contexts)},
                        "memory_usage": {
                            "sessions_mb": self._estimate_size(self._sessions) / 1024 / 1024,
                            "puzzles_mb": self._estimate_size(self._puzzles) / 1024 / 1024,
                            "recommendations_mb": self._estimate_size(self._recommendations) / 1024 / 1024,
                        },
                    }

    def _estimate_size(self, obj: Any) -> int:
        """Estimate memory size of object (rough approximation)."""
        try:
            import sys

            return sys.getsizeof(str(obj))
        except Exception:
            return 0

    # Cleanup operations

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval.total_seconds())
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}", exc_info=True)

    async def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions."""
        async with self._cleanup_lock:
            now = datetime.now()
            expired_sessions = []

            async with self._session_lock:
                for session_id, access_time in self._session_access_times.items():
                    if now - access_time > self.session_ttl:
                        expired_sessions.append(session_id)

            for session_id in expired_sessions:
                await self.delete_session(session_id)

            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    async def _cleanup_old_sessions(self) -> None:
        """Clean up oldest sessions when limit is reached."""
        # Sort sessions by access time and remove oldest
        session_times = sorted(self._session_access_times.items(), key=lambda x: x[1])

        # Remove oldest 10% to make room
        to_remove = max(1, len(session_times) // 10)
        for session_id, _ in session_times[:to_remove]:
            await self.delete_session(session_id)

        logger.info(f"Cleaned up {to_remove} old sessions to free space")

    # Persistence operations

    def _load_from_persistence(self) -> None:
        """Load data from persistence file."""
        try:
            import os

            if not os.path.exists(self.persistence_file):
                logger.info("No persistence file found, starting with empty storage")
                return

            with open(self.persistence_file, "r") as f:
                data = json.load(f)

            # Restore sessions
            for session_data in data.get("sessions", []):
                session = Session.parse_obj(session_data)
                self._sessions[session.id] = session
                self._session_access_times[session.id] = datetime.now()

            # Restore puzzles
            for puzzle_data in data.get("puzzles", []):
                puzzle = Puzzle.parse_obj(puzzle_data)
                self._puzzles[puzzle.id] = puzzle

            # Restore recommendations
            for rec_data in data.get("recommendations", []):
                recommendation = Recommendation.parse_obj(rec_data)
                self._recommendations[recommendation.id] = recommendation
                self._recommendations_by_session[recommendation.session_id].append(recommendation.id)

            logger.info(
                f"Loaded {len(self._sessions)} sessions, {len(self._puzzles)} puzzles, "
                f"{len(self._recommendations)} recommendations from persistence"
            )

        except Exception as e:
            logger.error(f"Failed to load from persistence: {e}", exc_info=True)

    async def _save_to_persistence(self) -> None:
        """Save data to persistence file."""
        try:
            data = {
                "sessions": [s.dict() for s in self._sessions.values()],
                "puzzles": [p.dict() for p in self._puzzles.values()],
                "recommendations": [r.dict() for r in self._recommendations.values()],
                "timestamp": datetime.now().isoformat(),
            }

            with open(self.persistence_file, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info("Data saved to persistence file")

        except Exception as e:
            logger.error(f"Failed to save to persistence: {e}", exc_info=True)


# Global storage instance
_storage_instance: Optional[InMemoryStorage] = None


def get_storage() -> InMemoryStorage:
    """Get the global storage instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = InMemoryStorage()
    return _storage_instance


async def initialize_storage(**kwargs) -> InMemoryStorage:
    """Initialize and start the storage system."""
    global _storage_instance
    _storage_instance = InMemoryStorage(**kwargs)
    await _storage_instance.start()
    return _storage_instance


async def cleanup_storage() -> None:
    """Clean up and stop the storage system."""
    global _storage_instance
    if _storage_instance:
        await _storage_instance.stop()
        _storage_instance = None
