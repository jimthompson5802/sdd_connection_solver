"""Context service for managing AI recommendation context data."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from ..models.ai_context import AIRecommendationContext
from ..models.group import Group
from ..models.one_away_group import OneAwayGroup
from ..models.session import Session


class ContextService:
    """Service for managing AI recommendation context and state.

    Provides functionality to:
    - Create and manage AI recommendation contexts
    - Update context based on game state changes
    - Generate context-aware prompt templates
    - Track context evolution during game sessions
    """

    def __init__(self):
        """Initialize context service with in-memory storage."""
        self._contexts: Dict[str, AIRecommendationContext] = {}
        self._default_prompt_template = self._get_default_prompt_template()

    def create_context_for_session(
        self, session: Session, initial_words: Optional[List[str]] = None
    ) -> AIRecommendationContext:
        """Create initial AI context for a new session.

        Args:
            session: Session to create context for
            initial_words: Initial puzzle words (defaults to session's remaining_words)

        Returns:
            New AI recommendation context instance
        """
        remaining_words = initial_words or session.remaining_words

        context = AIRecommendationContext(
            session_id=session.id,
            remaining_words=remaining_words.copy(),
            incorrect_groups=[],
            one_away_groups=[],
            solved_groups=[],
            llm_prompt_template=self._default_prompt_template,
        )

        # Store context
        self._contexts[session.id] = context

        return context

    def get_context_for_session(self, session_id: str) -> Optional[AIRecommendationContext]:
        """Retrieve AI context for a session.

        Args:
            session_id: Session identifier

        Returns:
            AI context if found, None otherwise
        """
        return self._contexts.get(session_id)

    def update_context_with_solved_group(
        self, session_id: str, solved_words: List[str], theme: str, difficulty_level: str = "yellow"
    ) -> Optional[AIRecommendationContext]:
        """Update context when a group is correctly solved.

        Args:
            session_id: Session identifier
            solved_words: The 4 words that were correctly grouped
            theme: The connection theme/explanation
            difficulty_level: Difficulty level of the solved group ("yellow", "green", "blue", "purple")

        Returns:
            Updated context or None if session not found
        """
        context = self._contexts.get(session_id)
        if not context:
            return None

        # Create solved group
        solved_group = Group(words=solved_words, theme=theme, difficulty=difficulty_level, is_solved=True)

        # Update context
        context.solved_groups.append(solved_group)
        context.remaining_words = [word for word in context.remaining_words if word not in solved_words]
        context.created_at = datetime.now()

        return context

    def update_context_with_incorrect_group(
        self, session_id: str, incorrect_words: List[str]
    ) -> Optional[AIRecommendationContext]:
        """Update context with an incorrect group attempt.

        Args:
            session_id: Session identifier
            incorrect_words: The 4 words that were incorrectly grouped

        Returns:
            Updated context or None if session not found
        """
        context = self._contexts.get(session_id)
        if not context:
            return None

        # Add to incorrect groups if not already present
        if incorrect_words not in context.incorrect_groups:
            context.incorrect_groups.append(incorrect_words)
            context.created_at = datetime.now()

        return context

    def update_context_with_one_away_group(
        self,
        session_id: str,
        attempted_words: List[str],
        correct_connection: Optional[str] = None,
        incorrect_word_hint: Optional[str] = None,
    ) -> Optional[AIRecommendationContext]:
        """Update context with a one-away group (3 correct, 1 incorrect).

        Args:
            session_id: Session identifier
            attempted_words: The 4 words that were attempted
            correct_connection: Hint about the correct connection (optional)
            incorrect_word_hint: Hint about which word was wrong (optional)

        Returns:
            Updated context or None if session not found
        """
        context = self._contexts.get(session_id)
        if not context:
            return None

        # Create one-away group
        one_away_group = OneAwayGroup(
            words=attempted_words,
            explanation=correct_connection if correct_connection else f"One away group: {', '.join(attempted_words)}",
        )

        # Add to one-away groups if not already present
        existing_attempts = [group.words for group in context.one_away_groups]
        if attempted_words not in existing_attempts:
            context.one_away_groups.append(one_away_group)
            context.created_at = datetime.now()

        return context

    def generate_context_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Generate a summary of the current context state.

        Args:
            session_id: Session identifier

        Returns:
            Context summary dictionary or None if session not found
        """
        context = self._contexts.get(session_id)
        if not context:
            return None

        return {
            "session_id": session_id,
            "remaining_words_count": len(context.remaining_words),
            "remaining_words": context.remaining_words,
            "solved_groups_count": len(context.solved_groups),
            "solved_groups": [
                {
                    "words": group.words,
                    "theme": group.theme,
                    "difficulty": group.difficulty,
                    "is_solved": group.is_solved,
                }
                for group in context.solved_groups
            ],
            "incorrect_attempts_count": len(context.incorrect_groups),
            "incorrect_groups": context.incorrect_groups,
            "one_away_attempts_count": len(context.one_away_groups),
            "one_away_groups": [
                {
                    "words": group.words,
                    "explanation": group.explanation,
                }
                for group in context.one_away_groups
            ],
            "last_updated": context.created_at.isoformat(),
            "prompt_template_length": len(context.llm_prompt_template),
        }

    def update_prompt_template(self, session_id: str, new_template: str) -> bool:
        """Update the prompt template for a session's context.

        Args:
            session_id: Session identifier
            new_template: New prompt template string

        Returns:
            True if template was updated, False if session not found
        """
        context = self._contexts.get(session_id)
        if not context:
            return False

        context.llm_prompt_template = new_template
        context.created_at = datetime.now()
        return True

    def get_context_statistics(self) -> Dict[str, Any]:
        """Get statistics about all managed contexts.

        Returns:
            Dictionary with context statistics
        """
        if not self._contexts:
            return {
                "total_contexts": 0,
                "active_sessions": 0,
                "average_solved_groups": 0.0,
                "average_incorrect_attempts": 0.0,
                "average_one_away_attempts": 0.0,
            }

        total_contexts = len(self._contexts)
        active_sessions = len([c for c in self._contexts.values() if len(c.remaining_words) > 0])

        solved_groups_counts = [len(c.solved_groups) for c in self._contexts.values()]
        incorrect_counts = [len(c.incorrect_groups) for c in self._contexts.values()]
        one_away_counts = [len(c.one_away_groups) for c in self._contexts.values()]

        return {
            "total_contexts": total_contexts,
            "active_sessions": active_sessions,
            "average_solved_groups": sum(solved_groups_counts) / total_contexts,
            "average_incorrect_attempts": sum(incorrect_counts) / total_contexts,
            "average_one_away_attempts": sum(one_away_counts) / total_contexts,
        }

    def cleanup_completed_contexts(self, max_age_hours: int = 24) -> int:
        """Remove contexts for completed or old sessions.

        Args:
            max_age_hours: Maximum age in hours before cleanup

        Returns:
            Number of contexts cleaned up
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        contexts_to_remove = []
        for session_id, context in self._contexts.items():
            # Remove if completed (no remaining words) or too old
            if len(context.remaining_words) == 0 or context.created_at < cutoff_time:
                contexts_to_remove.append(session_id)

        for session_id in contexts_to_remove:
            del self._contexts[session_id]

        return len(contexts_to_remove)

    def _get_default_prompt_template(self) -> str:
        """Get the default prompt template for AI recommendations.

        Returns:
            Default prompt template string
        """
        return """
        You are an expert at solving NYT Connections puzzles. Analyze the remaining words and identify
        a group of exactly 4 words that share a common theme or connection.

        Consider the following context:
        - Previously solved groups: {solved_groups}
        - Previously incorrect attempts: {incorrect_groups}
        - One-away attempts (3 correct, 1 wrong): {one_away_groups}

        Remaining words: {remaining_words}

        Provide your response in this format:
        WORDS: [word1, word2, word3, word4]
        EXPLANATION: Brief explanation of the connection
        """.strip()

    def reset_context(self, session_id: str) -> bool:
        """Reset context to initial state for a session.

        Args:
            session_id: Session to reset

        Returns:
            True if context was reset, False if session not found
        """
        context = self._contexts.get(session_id)
        if not context:
            return False

        # Reset to initial state but keep session_id and original words
        original_words = context.remaining_words + [word for group in context.solved_groups for word in group.words]

        context.remaining_words = original_words
        context.solved_groups = []
        context.incorrect_groups = []
        context.one_away_groups = []
        context.created_at = datetime.now()

        return True

    def delete_context(self, session_id: str) -> bool:
        """Delete context for a session.

        Args:
            session_id: Session identifier

        Returns:
            True if context was deleted, False if not found
        """
        if session_id in self._contexts:
            del self._contexts[session_id]
            return True
        return False
