"""Evaluation service for processing user feedback on AI recommendations."""

from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from ..models.recommendation import Recommendation
from ..models.ai_context import AIRecommendationContext
from ..models.one_away_group import OneAwayGroup
from ..models.group import Group


class EvaluationService:
    """Service for processing user evaluations and updating game context.

    Provides functionality to:
    - Process correct, incorrect, and one-away evaluations
    - Update AI recommendation context based on feedback
    - Generate learning insights from evaluation patterns
    - Track evaluation statistics and performance
    """

    def __init__(self):
        """Initialize evaluation service."""
        self._evaluation_history: Dict[str, List[Dict[str, Any]]] = {}

    def evaluate_recommendation(
        self, recommendation: Recommendation, evaluation: str, context: Optional[AIRecommendationContext] = None
    ) -> Tuple[Recommendation, Optional[AIRecommendationContext]]:
        """Process user evaluation of a recommendation.

        Args:
            recommendation: The recommendation being evaluated
            evaluation: User's evaluation ("correct", "incorrect", "one_away")
            context: Current AI context to update (optional)

        Returns:
            Tuple of (updated_recommendation, updated_context)

        Raises:
            ValueError: If evaluation is invalid
        """
        if evaluation not in ["correct", "incorrect", "one_away"]:
            raise ValueError(f"Invalid evaluation: {evaluation}. Must be 'correct', 'incorrect', or 'one_away'")

        # Update recommendation with evaluation
        recommendation.user_evaluation = evaluation
        recommendation.evaluation_timestamp = datetime.now()

        # Update context based on evaluation type
        updated_context = None
        if context:
            updated_context = self._update_context_from_evaluation(context, recommendation, evaluation)

        # Record evaluation in history
        self._record_evaluation_history(recommendation, evaluation)

        return recommendation, updated_context

    def _update_context_from_evaluation(
        self, context: AIRecommendationContext, recommendation: Recommendation, evaluation: str
    ) -> AIRecommendationContext:
        """Update AI context based on user evaluation.

        Args:
            context: Current context to update
            recommendation: The evaluated recommendation
            evaluation: Type of evaluation

        Returns:
            Updated context with new information
        """
        # Create a copy of the context to avoid modifying the original
        updated_context = AIRecommendationContext(
            session_id=context.session_id,
            remaining_words=context.remaining_words.copy(),
            incorrect_groups=context.incorrect_groups.copy(),
            one_away_groups=context.one_away_groups.copy(),
            solved_groups=context.solved_groups.copy(),
            llm_prompt_template=context.llm_prompt_template,
            created_at=datetime.now(),
        )

        if evaluation == "correct":
            # Add to solved groups and remove words from remaining
            solved_group = Group(
                words=recommendation.recommended_words,
                theme=recommendation.explanation,
                difficulty="yellow",  # Default difficulty
            )
            updated_context.solved_groups.append(solved_group)

            # Remove solved words from remaining words
            updated_context.remaining_words = [
                word for word in updated_context.remaining_words if word not in recommendation.recommended_words
            ]

        elif evaluation == "incorrect":
            # Add to incorrect groups to avoid in future
            updated_context.incorrect_groups.append(recommendation.recommended_words)

        elif evaluation == "one_away":
            # Add to one-away groups for future reference
            one_away_group = OneAwayGroup(
                attempted_words=recommendation.recommended_words,
                correct_connection=None,  # Could be populated later with hints
                incorrect_word_hint=None,
            )
            updated_context.one_away_groups.append(one_away_group)

        return updated_context

    def _record_evaluation_history(self, recommendation: Recommendation, evaluation: str) -> None:
        """Record evaluation in history for analytics.

        Args:
            recommendation: The evaluated recommendation
            evaluation: Type of evaluation
        """
        session_id = recommendation.session_id

        if session_id not in self._evaluation_history:
            self._evaluation_history[session_id] = []

        timestamp = recommendation.evaluation_timestamp.isoformat() if recommendation.evaluation_timestamp else None

        evaluation_record = {
            "recommendation_id": recommendation.id,
            "recommended_words": recommendation.recommended_words,
            "evaluation": evaluation,
            "timestamp": timestamp,
            "llm_model": recommendation.llm_model,
            "processing_time_ms": recommendation.processing_time_ms,
            "explanation": recommendation.explanation,
        }

        self._evaluation_history[session_id].append(evaluation_record)

    def get_evaluation_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get evaluation statistics for a session.

        Args:
            session_id: Session to analyze

        Returns:
            Dictionary with evaluation statistics
        """
        if session_id not in self._evaluation_history:
            return {
                "total_evaluations": 0,
                "correct_count": 0,
                "incorrect_count": 0,
                "one_away_count": 0,
                "accuracy_rate": 0.0,
                "average_processing_time_ms": 0,
            }

        evaluations = self._evaluation_history[session_id]
        total = len(evaluations)

        if total == 0:
            return {
                "total_evaluations": 0,
                "correct_count": 0,
                "incorrect_count": 0,
                "one_away_count": 0,
                "accuracy_rate": 0.0,
                "average_processing_time_ms": 0,
            }

        correct_count = sum(1 for e in evaluations if e["evaluation"] == "correct")
        incorrect_count = sum(1 for e in evaluations if e["evaluation"] == "incorrect")
        one_away_count = sum(1 for e in evaluations if e["evaluation"] == "one_away")

        accuracy_rate = correct_count / total if total > 0 else 0.0
        avg_processing_time = sum(e["processing_time_ms"] for e in evaluations) / total

        return {
            "total_evaluations": total,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "one_away_count": one_away_count,
            "accuracy_rate": accuracy_rate,
            "average_processing_time_ms": int(avg_processing_time),
        }

    def analyze_learning_patterns(self, session_id: str) -> Dict[str, Any]:
        """Analyze learning patterns from evaluation history.

        Args:
            session_id: Session to analyze

        Returns:
            Dictionary with learning pattern insights
        """
        if session_id not in self._evaluation_history:
            return {"insights": [], "recommendations": []}

        evaluations = self._evaluation_history[session_id]
        insights = []
        recommendations = []

        if len(evaluations) >= 3:
            # Check for improvement over time
            recent_accuracy = self._calculate_recent_accuracy(evaluations, window=3)
            overall_accuracy = sum(1 for e in evaluations if e["evaluation"] == "correct") / len(evaluations)

            if recent_accuracy > overall_accuracy + 0.2:
                insights.append("AI is showing improvement in recent recommendations")

            # Check for processing time trends
            recent_times = [e["processing_time_ms"] for e in evaluations[-3:]]
            avg_recent_time = sum(recent_times) / len(recent_times)

            if avg_recent_time > 2000:
                recommendations.append("Consider using faster LLM model for better response times")

            # Check for one-away pattern
            one_away_count = sum(1 for e in evaluations if e["evaluation"] == "one_away")
            if one_away_count > len(evaluations) * 0.3:
                insights.append("High one-away rate suggests AI is close but needs refinement")
                recommendations.append("Enable more detailed context sharing for one-away groups")

        return {
            "insights": insights,
            "recommendations": recommendations,
            "evaluation_trend": self._get_evaluation_trend(evaluations),
        }

    def _calculate_recent_accuracy(self, evaluations: List[Dict[str, Any]], window: int = 3) -> float:
        """Calculate accuracy for recent evaluations.

        Args:
            evaluations: List of evaluation records
            window: Number of recent evaluations to consider

        Returns:
            Accuracy rate for recent evaluations
        """
        if len(evaluations) < window:
            window = len(evaluations)

        recent_evaluations = evaluations[-window:]
        correct_count = sum(1 for e in recent_evaluations if e["evaluation"] == "correct")

        return correct_count / window if window > 0 else 0.0

    def _get_evaluation_trend(self, evaluations: List[Dict[str, Any]]) -> str:
        """Determine the trend in evaluation quality.

        Args:
            evaluations: List of evaluation records

        Returns:
            Trend description ("improving", "declining", "stable")
        """
        if len(evaluations) < 4:
            return "insufficient_data"

        # Compare first half vs second half
        mid_point = len(evaluations) // 2
        first_half = evaluations[:mid_point]
        second_half = evaluations[mid_point:]

        first_accuracy = sum(1 for e in first_half if e["evaluation"] == "correct") / len(first_half)
        second_accuracy = sum(1 for e in second_half if e["evaluation"] == "correct") / len(second_half)

        if second_accuracy > first_accuracy + 0.1:
            return "improving"
        elif second_accuracy < first_accuracy - 0.1:
            return "declining"
        else:
            return "stable"

    def get_session_evaluation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get complete evaluation history for a session.

        Args:
            session_id: Session to retrieve history for

        Returns:
            List of evaluation records
        """
        return self._evaluation_history.get(session_id, [])

    def clear_session_history(self, session_id: str) -> bool:
        """Clear evaluation history for a session.

        Args:
            session_id: Session to clear

        Returns:
            True if history was cleared, False if session not found
        """
        if session_id in self._evaluation_history:
            del self._evaluation_history[session_id]
            return True
        return False
