"""Unit tests for evaluation processing logic."""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.services.evaluation_service import EvaluationService
from src.models.recommendation import Recommendation
from src.models.ai_context import AIRecommendationContext
from src.models.group import Group


class TestEvaluationService:
    """Test cases for EvaluationService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = EvaluationService()

    def test_init(self):
        """Test EvaluationService initialization."""
        assert self.service._evaluation_history == {}

    def test_evaluate_recommendation_correct(self):
        """Test evaluating a recommendation as correct."""
        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "banana", "cherry", "date"],
            explanation="Types of fruit",
            llm_model="gpt-4",
            processing_time_ms=1500,
        )

        context = AIRecommendationContext(
            session_id="session_1",
            remaining_words=["apple", "banana", "cherry", "date", "cat", "dog", "bird", "fish"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
        )

        with patch("src.services.evaluation_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)

            updated_rec, updated_context = self.service.evaluate_recommendation(recommendation, "correct", context)

        # Check recommendation was updated
        assert updated_rec.user_evaluation == "correct"
        assert updated_rec.evaluation_timestamp == datetime(2023, 1, 1, 12, 0, 0)

        # Check context was updated
        assert updated_context is not None
        assert len(updated_context.solved_groups) == 1
        assert updated_context.solved_groups[0].words == ["apple", "banana", "cherry", "date"]
        assert updated_context.solved_groups[0].theme == "Types of fruit"
        assert updated_context.remaining_words == ["cat", "dog", "bird", "fish"]

    def test_evaluate_recommendation_incorrect(self):
        """Test evaluating a recommendation as incorrect."""
        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "cat", "cherry", "date"],
            explanation="Random words",
            llm_model="gpt-4",
            processing_time_ms=1500,
        )

        context = AIRecommendationContext(
            session_id="session_1",
            remaining_words=["apple", "banana", "cherry", "date", "cat", "dog", "bird", "fish"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
        )

        updated_rec, updated_context = self.service.evaluate_recommendation(recommendation, "incorrect", context)

        # Check recommendation was updated
        assert updated_rec.user_evaluation == "incorrect"
        assert updated_rec.evaluation_timestamp is not None

        # Check context was updated
        assert updated_context is not None
        assert len(updated_context.incorrect_groups) == 1
        assert updated_context.incorrect_groups[0] == ["apple", "cat", "cherry", "date"]
        assert updated_context.remaining_words == ["apple", "banana", "cherry", "date", "cat", "dog", "bird", "fish"]

    def test_evaluate_recommendation_one_away(self):
        """Test evaluating a recommendation as one away."""
        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "banana", "cherry", "grape"],
            explanation="Types of fruit",
            llm_model="gpt-4",
            processing_time_ms=1500,
        )

        context = AIRecommendationContext(
            session_id="session_1",
            remaining_words=["apple", "banana", "cherry", "date", "grape", "dog", "bird", "fish"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
        )

        updated_rec, updated_context = self.service.evaluate_recommendation(recommendation, "one_away", context)

        # Check recommendation was updated
        assert updated_rec.user_evaluation == "one_away"
        assert updated_rec.evaluation_timestamp is not None

        # Check context was updated
        assert updated_context is not None
        assert len(updated_context.one_away_groups) == 1
        assert updated_context.one_away_groups[0].attempted_words == ["apple", "banana", "cherry", "grape"]
        assert updated_context.remaining_words == ["apple", "banana", "cherry", "date", "grape", "dog", "bird", "fish"]

    def test_evaluate_recommendation_invalid_evaluation(self):
        """Test evaluating a recommendation with invalid evaluation type."""
        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "banana", "cherry", "date"],
            explanation="Types of fruit",
            llm_model="gpt-4",
            processing_time_ms=1500,
        )

        with pytest.raises(ValueError, match="Invalid evaluation: invalid"):
            self.service.evaluate_recommendation(recommendation, "invalid")

    def test_evaluate_recommendation_without_context(self):
        """Test evaluating a recommendation without providing context."""
        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "banana", "cherry", "date"],
            explanation="Types of fruit",
            llm_model="gpt-4",
            processing_time_ms=1500,
        )

        updated_rec, updated_context = self.service.evaluate_recommendation(recommendation, "correct")

        # Check recommendation was updated
        assert updated_rec.user_evaluation == "correct"
        assert updated_rec.evaluation_timestamp is not None

        # Check context is None
        assert updated_context is None

    def test_record_evaluation_history(self):
        """Test recording evaluation history."""
        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "banana", "cherry", "date"],
            explanation="Types of fruit",
            llm_model="gpt-4",
            processing_time_ms=1500,
        )

        self.service.evaluate_recommendation(recommendation, "correct")

        history = self.service.get_session_evaluation_history("session_1")
        assert len(history) == 1
        assert history[0]["recommendation_id"] == "rec_1"
        assert history[0]["evaluation"] == "correct"
        assert history[0]["recommended_words"] == ["apple", "banana", "cherry", "date"]

    def test_get_evaluation_statistics_empty(self):
        """Test getting evaluation statistics for empty session."""
        stats = self.service.get_evaluation_statistics("nonexistent_session")

        expected = {
            "total_evaluations": 0,
            "correct_count": 0,
            "incorrect_count": 0,
            "one_away_count": 0,
            "accuracy_rate": 0.0,
            "average_processing_time_ms": 0,
        }

        assert stats == expected

    def test_get_evaluation_statistics_with_data(self):
        """Test getting evaluation statistics with evaluation data."""
        # Add multiple evaluations
        for i, evaluation in enumerate(["correct", "incorrect", "one_away", "correct"]):
            recommendation = Recommendation(
                id=f"rec_{i}",
                session_id="session_1",
                recommended_words=[f"word{j}" for j in range(i * 4, (i + 1) * 4)],
                explanation=f"Explanation {i}",
                llm_model="gpt-4",
                processing_time_ms=1000 + i * 200,
            )
            self.service.evaluate_recommendation(recommendation, evaluation)

        stats = self.service.get_evaluation_statistics("session_1")

        assert stats["total_evaluations"] == 4
        assert stats["correct_count"] == 2
        assert stats["incorrect_count"] == 1
        assert stats["one_away_count"] == 1
        assert stats["accuracy_rate"] == 0.5  # 2/4
        assert stats["average_processing_time_ms"] == 1300  # (1000+1200+1400+1600)/4

    def test_analyze_learning_patterns_insufficient_data(self):
        """Test analyzing learning patterns with insufficient data."""
        # Add only 2 evaluations
        for i, evaluation in enumerate(["correct", "incorrect"]):
            recommendation = Recommendation(
                id=f"rec_{i}",
                session_id="session_1",
                recommended_words=[f"word{j}" for j in range(i * 4, (i + 1) * 4)],
                explanation=f"Explanation {i}",
                llm_model="gpt-4",
                processing_time_ms=1000,
            )
            self.service.evaluate_recommendation(recommendation, evaluation)

        patterns = self.service.analyze_learning_patterns("session_1")

        assert patterns["insights"] == []
        assert patterns["recommendations"] == []

    def test_analyze_learning_patterns_improvement(self):
        """Test analyzing learning patterns showing improvement."""
        # Add evaluations showing improvement
        evaluations = ["incorrect", "incorrect", "correct", "correct"]
        for i, evaluation in enumerate(evaluations):
            recommendation = Recommendation(
                id=f"rec_{i}",
                session_id="session_1",
                recommended_words=[f"word{j}" for j in range(i * 4, (i + 1) * 4)],
                explanation=f"Explanation {i}",
                llm_model="gpt-4",
                processing_time_ms=1000,
            )
            self.service.evaluate_recommendation(recommendation, evaluation)

        patterns = self.service.analyze_learning_patterns("session_1")

        assert any("improvement" in insight for insight in patterns["insights"])

    def test_analyze_learning_patterns_high_one_away(self):
        """Test analyzing learning patterns with high one-away rate."""
        # Add evaluations with high one-away rate
        evaluations = ["one_away", "one_away", "correct"]
        for i, evaluation in enumerate(evaluations):
            recommendation = Recommendation(
                id=f"rec_{i}",
                session_id="session_1",
                recommended_words=[f"word{j}" for j in range(i * 4, (i + 1) * 4)],
                explanation=f"Explanation {i}",
                llm_model="gpt-4",
                processing_time_ms=1000,
            )
            self.service.evaluate_recommendation(recommendation, evaluation)

        patterns = self.service.analyze_learning_patterns("session_1")

        assert any("one-away rate" in insight for insight in patterns["insights"])
        assert any("context sharing" in rec for rec in patterns["recommendations"])

    def test_analyze_learning_patterns_slow_processing(self):
        """Test analyzing learning patterns with slow processing times."""
        # Add evaluations with slow processing times
        for i in range(3):
            recommendation = Recommendation(
                id=f"rec_{i}",
                session_id="session_1",
                recommended_words=[f"word{j}" for j in range(i * 4, (i + 1) * 4)],
                explanation=f"Explanation {i}",
                llm_model="gpt-4",
                processing_time_ms=3000,  # Slow processing
            )
            self.service.evaluate_recommendation(recommendation, "correct")

        patterns = self.service.analyze_learning_patterns("session_1")

        assert any("faster LLM model" in rec for rec in patterns["recommendations"])

    def test_calculate_recent_accuracy(self):
        """Test calculating recent accuracy."""
        evaluations = [
            {"evaluation": "incorrect"},
            {"evaluation": "incorrect"},
            {"evaluation": "correct"},
            {"evaluation": "correct"},
            {"evaluation": "correct"},
        ]

        # Test with default window of 3
        accuracy = self.service._calculate_recent_accuracy(evaluations)
        assert accuracy == 1.0  # Last 3 are all correct

        # Test with window of 2
        accuracy = self.service._calculate_recent_accuracy(evaluations, window=2)
        assert accuracy == 1.0  # Last 2 are all correct

        # Test with window larger than available data
        accuracy = self.service._calculate_recent_accuracy(evaluations, window=10)
        assert accuracy == 0.6  # 3 out of 5 correct

    def test_get_evaluation_trend(self):
        """Test getting evaluation trend."""
        # Test improving trend
        improving_evals = [
            {"evaluation": "incorrect"},
            {"evaluation": "incorrect"},
            {"evaluation": "correct"},
            {"evaluation": "correct"},
        ]
        trend = self.service._get_evaluation_trend(improving_evals)
        assert trend == "improving"

        # Test declining trend
        declining_evals = [
            {"evaluation": "correct"},
            {"evaluation": "correct"},
            {"evaluation": "incorrect"},
            {"evaluation": "incorrect"},
        ]
        trend = self.service._get_evaluation_trend(declining_evals)
        assert trend == "declining"

        # Test stable trend
        stable_evals = [
            {"evaluation": "correct"},
            {"evaluation": "incorrect"},
            {"evaluation": "correct"},
            {"evaluation": "incorrect"},
        ]
        trend = self.service._get_evaluation_trend(stable_evals)
        assert trend == "stable"

        # Test insufficient data
        insufficient_evals = [{"evaluation": "correct"}, {"evaluation": "incorrect"}]
        trend = self.service._get_evaluation_trend(insufficient_evals)
        assert trend == "insufficient_data"

    def test_get_session_evaluation_history(self):
        """Test getting session evaluation history."""
        # Test empty history
        history = self.service.get_session_evaluation_history("nonexistent")
        assert history == []

        # Test with data
        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "banana", "cherry", "date"],
            explanation="Types of fruit",
            llm_model="gpt-4",
            processing_time_ms=1500,
        )

        self.service.evaluate_recommendation(recommendation, "correct")
        history = self.service.get_session_evaluation_history("session_1")

        assert len(history) == 1
        assert history[0]["recommendation_id"] == "rec_1"

    def test_clear_session_history(self):
        """Test clearing session history."""
        # Add some history
        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "banana", "cherry", "date"],
            explanation="Types of fruit",
            llm_model="gpt-4",
            processing_time_ms=1500,
        )

        self.service.evaluate_recommendation(recommendation, "correct")
        assert len(self.service.get_session_evaluation_history("session_1")) == 1

        # Clear existing session
        result = self.service.clear_session_history("session_1")
        assert result is True
        assert len(self.service.get_session_evaluation_history("session_1")) == 0

        # Clear non-existent session
        result = self.service.clear_session_history("nonexistent")
        assert result is False

    def test_context_update_preserves_original(self):
        """Test that context updates don't modify the original context."""
        original_context = AIRecommendationContext(
            session_id="session_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
        )

        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "banana", "cherry", "date"],
            explanation="Types of fruit",
            llm_model="gpt-4",
            processing_time_ms=1500,
        )

        original_remaining_count = len(original_context.remaining_words)
        original_solved_count = len(original_context.solved_groups)

        _, updated_context = self.service.evaluate_recommendation(recommendation, "correct", original_context)

        # Original context should be unchanged
        assert len(original_context.remaining_words) == original_remaining_count
        assert len(original_context.solved_groups) == original_solved_count

        # Updated context should be different
        assert updated_context is not None
        assert len(updated_context.remaining_words) < original_remaining_count
        assert len(updated_context.solved_groups) > original_solved_count

    def test_evaluation_with_existing_solved_groups(self):
        """Test evaluation when context already has solved groups."""
        existing_group = Group(words=["red", "blue", "green", "yellow"], theme="Colors", difficulty_level=1, position=1)

        context = AIRecommendationContext(
            session_id="session_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[existing_group],
            incorrect_groups=[],
            one_away_groups=[],
        )

        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "banana", "cherry", "date"],
            explanation="Types of fruit",
            llm_model="gpt-4",
            processing_time_ms=1500,
        )

        _, updated_context = self.service.evaluate_recommendation(recommendation, "correct", context)

        # Should have 2 solved groups now
        assert updated_context is not None
        assert len(updated_context.solved_groups) == 2
        assert updated_context.solved_groups[0] == existing_group  # Original group preserved
        assert updated_context.solved_groups[1].words == ["apple", "banana", "cherry", "date"]
        assert updated_context.solved_groups[1].position == 2

    def test_evaluation_statistics_edge_cases(self):
        """Test evaluation statistics with edge cases."""
        # Test with zero processing times
        recommendation = Recommendation(
            id="rec_1",
            session_id="session_1",
            recommended_words=["apple", "banana", "cherry", "date"],
            explanation="Types of fruit",
            llm_model="gpt-4",
            processing_time_ms=0,
        )

        self.service.evaluate_recommendation(recommendation, "correct")
        stats = self.service.get_evaluation_statistics("session_1")

        assert stats["average_processing_time_ms"] == 0
