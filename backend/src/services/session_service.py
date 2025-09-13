"""Session service for game state management functionality."""

from datetime import datetime
from typing import List, Optional

from ..models.session import Session
from ..models.recommendation import Recommendation


class SessionService:
    """Service for managing game sessions and state.

    Provides functionality to:
    - Create and manage game sessions
    - Track session progress and state
    - Update remaining words as groups are solved
    - Manage recommendation history
    - Handle session completion and failures
    """

    def __init__(self):
        """Initialize session service with in-memory storage."""
        self._sessions: dict[str, Session] = {}

    def create_session(
        self, puzzle_id: str, llm_model: str, user_id: Optional[str] = None, initial_words: Optional[List[str]] = None
    ) -> Session:
        """Create a new game session.

        Args:
            puzzle_id: Reference to puzzle being solved
            llm_model: LLM model configuration for recommendations
            user_id: Optional user identifier
            initial_words: Initial 16 words from puzzle (if not provided, assumes all 16 words)

        Returns:
            New session instance

        Raises:
            ValueError: If parameters are invalid
        """
        if not puzzle_id:
            raise ValueError("puzzle_id is required")
        if not llm_model:
            raise ValueError("llm_model is required")

        # Default to empty word list if not provided (will be set from puzzle)
        remaining_words = initial_words or []
        if len(remaining_words) == 0:
            # For now, create placeholder words - in real implementation would fetch from puzzle
            remaining_words = [f"word_{i + 1}" for i in range(16)]

        session = Session(puzzle_id=puzzle_id, llm_model_config=llm_model, remaining_words=remaining_words)

        # Store session
        self._sessions[session.id] = session

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve session by ID.

        Args:
            session_id: Unique session identifier

        Returns:
            Session instance if found, None otherwise
        """
        return self._sessions.get(session_id)

    def update_session_activity(self, session_id: str) -> bool:
        """Update the last_activity timestamp for a session.

        Args:
            session_id: Session to update

        Returns:
            True if session was found and updated, False otherwise
        """
        session = self._sessions.get(session_id)
        if session:
            session.last_activity = datetime.now()
            return True
        return False

    def add_recommendation_to_session(self, session_id: str, recommendation: Recommendation) -> bool:
        """Add a recommendation to session history.

        Args:
            session_id: Session to update
            recommendation: Recommendation to add

        Returns:
            True if recommendation was added, False if session not found
        """
        session = self._sessions.get(session_id)
        if session:
            session.recommendation_history.append(recommendation)
            # Mark as pending until evaluated
            session.pending_recommendation_id = recommendation.id
            self.update_session_activity(session_id)
            return True
        return False

    def mark_recommendation_evaluated(self, session_id: str, recommendation_id: str, evaluation: str) -> bool:
        """Mark a recommendation as evaluated and update session pending state.

        Args:
            session_id: Session to update
            recommendation_id: Recommendation ID to mark evaluated
            evaluation: Evaluation value (correct|incorrect|one_away)

        Returns:
            True if updated, False if session or recommendation not found
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        updated = False
        for rec in session.recommendation_history:
            if rec.id == recommendation_id:
                rec.user_evaluation = evaluation
                from datetime import datetime

                rec.evaluation_timestamp = datetime.now()
                updated = True
                break

        # Clear pending recommendation id if it matches
        if session.pending_recommendation_id == recommendation_id:
            session.pending_recommendation_id = None

        if updated:
            self.update_session_activity(session_id)

        return updated

    def solve_group(self, session_id: str, solved_words: List[str]) -> bool:
        """Mark a group as solved and update session state.

        Args:
            session_id: Session to update
            solved_words: The 4 words that form the solved group

        Returns:
            True if group was marked as solved, False if session not found

        Raises:
            ValueError: If solved_words is not exactly 4 words
        """
        if len(solved_words) != 4:
            raise ValueError("solved_words must contain exactly 4 words")

        session = self._sessions.get(session_id)
        if not session:
            return False

        # First increment solved groups count, then update remaining words
        session.solved_groups_count += 1

        # Remove solved words from remaining words
        session.remaining_words = [word for word in session.remaining_words if word not in solved_words]

        # Check if puzzle is completed
        if session.solved_groups_count >= 4:
            session.status = "completed"

        self.update_session_activity(session_id)
        return True

    def increment_incorrect_evaluation(self, session_id: str) -> bool:
        """Increment incorrect evaluation count and check for failure.

        Args:
            session_id: Session to update

        Returns:
            True if count was incremented, False if session not found
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.incorrect_evaluation_count += 1

        # Check if session has failed (4 incorrect evaluations)
        if session.incorrect_evaluation_count >= 4:
            session.status = "failed"

        self.update_session_activity(session_id)
        return True

    def abandon_session(self, session_id: str) -> bool:
        """Mark a session as abandoned.

        Args:
            session_id: Session to abandon

        Returns:
            True if session was abandoned, False if session not found
        """
        session = self._sessions.get(session_id)
        if session:
            session.status = "abandoned"
            self.update_session_activity(session_id)
            return True
        return False

    def get_active_sessions(self, user_id: Optional[str] = None) -> List[Session]:
        """Get all active sessions, optionally filtered by user.

        Args:
            user_id: Optional user filter

        Returns:
            List of active sessions
        """
        active_sessions = [session for session in self._sessions.values() if session.status == "active"]

        if user_id:
            # Note: Session model doesn't have user_id field in current implementation
            # This would need to be added to Session model if user filtering is needed
            pass

        return active_sessions

    def get_session_statistics(self, session_id: str) -> Optional[dict]:
        """Get session statistics and progress.

        Args:
            session_id: Session to analyze

        Returns:
            Dictionary with session statistics or None if session not found
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session.id,
            "status": session.status,
            "solved_groups_count": session.solved_groups_count,
            "remaining_words_count": len(session.remaining_words),
            "incorrect_evaluation_count": session.incorrect_evaluation_count,
            "recommendation_count": len(session.recommendation_history),
            "session_duration_minutes": (datetime.now() - session.start_time).total_seconds() / 60,
            "last_activity": session.last_activity.isoformat(),
        }

    def get_all_sessions(self) -> List[Session]:
        """Get all stored sessions.

        Returns:
            List of all session instances
        """
        return list(self._sessions.values())

    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID.

        Args:
            session_id: Session identifier to delete

        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
