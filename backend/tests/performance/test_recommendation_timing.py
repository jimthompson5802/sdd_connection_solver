"""Performance tests for AI recommendation generation.

Tests to ensure AI recommendation generation meets performance requirements:
- Recommendation generation under 2 seconds
- Multiple concurrent recommendation requests
- Memory usage during recommendation generation
"""

import asyncio
import pytest
import time

from src.models.ai_context import AIRecommendationContext
from src.models.group import Group
from src.models.one_away_group import OneAwayGroup
from src.services.llm_service import LLMService
from src.llm.recommendation_engine import RecommendationEngine


class TestRecommendationTiming:
    """Test recommendation generation timing performance."""

    @pytest.fixture
    def sample_context(self) -> AIRecommendationContext:
        """Create sample AI context for testing."""
        return AIRecommendationContext(
            session_id="test-session-123",
            remaining_words=["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "kiwi"],
            solved_groups=[Group(words=["red", "blue", "green", "yellow"], theme="Colors", difficulty="yellow")],
            incorrect_groups=[["cat", "dog", "bird", "fish"]],
            one_away_groups=[
                OneAwayGroup(words=["tennis", "golf", "soccer", "hockey"], explanation="Sports that use balls")
            ],
            llm_prompt_template="standard",
        )

    @pytest.fixture
    def llm_service(self) -> LLMService:
        """Create LLM service for testing."""
        return LLMService()

    @pytest.fixture
    def recommendation_engine(self) -> RecommendationEngine:
        """Create recommendation engine for testing."""
        return RecommendationEngine(default_provider="mock")

    @pytest.mark.asyncio
    async def test_single_recommendation_under_2_seconds(
        self, llm_service: LLMService, sample_context: AIRecommendationContext
    ):
        """Test that single recommendation generation is under 2 seconds."""
        session_id = "test-session-timing"
        start_time = time.time()

        recommendation = await llm_service.generate_recommendation(
            session_id=session_id, context=sample_context, llm_model="gpt-4"
        )

        elapsed_time = time.time() - start_time

        # Performance requirement: under 2 seconds
        assert elapsed_time < 2.0, f"Recommendation took {elapsed_time:.2f}s, exceeds 2s limit"

        # Verify recommendation was generated
        assert recommendation is not None
        assert recommendation.session_id == session_id
        assert len(recommendation.recommended_words) == 4
        assert recommendation.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_recommendation_engine_under_2_seconds(
        self, recommendation_engine: RecommendationEngine, sample_context: AIRecommendationContext
    ):
        """Test that recommendation engine generation is under 2 seconds."""
        session_id = "test-engine-timing"
        start_time = time.time()

        recommendation = await recommendation_engine.generate_recommendation(
            session_id=session_id, ai_context=sample_context, llm_model="gpt-4"
        )

        elapsed_time = time.time() - start_time

        # Performance requirement: under 2 seconds
        assert elapsed_time < 2.0, f"Engine recommendation took {elapsed_time:.2f}s, exceeds 2s limit"

        # Verify recommendation was generated
        assert recommendation is not None
        assert recommendation.session_id == session_id

    @pytest.mark.asyncio
    async def test_multiple_models_timing(self, llm_service: LLMService, sample_context: AIRecommendationContext):
        """Test timing across different LLM models."""
        session_id = "test-multi-model-timing"
        models = ["gpt-4", "gpt-3.5-turbo", "claude-3"]

        for model in models:
            start_time = time.time()

            recommendation = await llm_service.generate_recommendation(
                session_id=session_id, context=sample_context, llm_model=model
            )

            elapsed_time = time.time() - start_time

            # Each model should be under 2 seconds
            assert elapsed_time < 2.0, f"Model {model} took {elapsed_time:.2f}s, exceeds 2s limit"
            assert recommendation.llm_model == model

    @pytest.mark.asyncio
    async def test_concurrent_recommendations_timing(
        self, llm_service: LLMService, sample_context: AIRecommendationContext
    ):
        """Test timing with concurrent recommendation requests."""
        session_ids = [f"test-concurrent-{i}" for i in range(5)]

        async def generate_single_recommendation(session_id: str) -> float:
            """Generate single recommendation and return elapsed time."""
            start_time = time.time()
            await llm_service.generate_recommendation(session_id=session_id, context=sample_context, llm_model="gpt-4")
            return time.time() - start_time

        start_time = time.time()

        # Run 5 concurrent recommendations
        tasks = [generate_single_recommendation(sid) for sid in session_ids]
        elapsed_times = await asyncio.gather(*tasks)

        total_elapsed = time.time() - start_time

        # Each individual recommendation should be under 2 seconds
        for i, elapsed in enumerate(elapsed_times):
            assert elapsed < 2.0, f"Concurrent recommendation {i} took {elapsed:.2f}s, exceeds 2s limit"

        # Total time should be reasonable (not linearly additive)
        assert total_elapsed < 5.0, f"Concurrent processing took {total_elapsed:.2f}s, should be better than sequential"

    @pytest.mark.asyncio
    async def test_large_context_timing(self, llm_service: LLMService):
        """Test timing with large context (many previous attempts)."""
        # Create large context with many previous attempts
        large_context = AIRecommendationContext(
            session_id="test-large-context-session",
            remaining_words=["word" + str(i) for i in range(16)],  # 16 remaining words
            solved_groups=[
                Group(words=[f"solved{i}_{j}" for j in range(4)], theme=f"Theme {i}", difficulty="yellow")
                for i in range(3)  # 3 solved groups
            ],
            incorrect_groups=[[f"wrong{i}_{j}" for j in range(4)] for i in range(10)],  # 10 incorrect attempts
            one_away_groups=[
                OneAwayGroup(words=[f"oneaway{i}_{j}" for j in range(4)], explanation=f"Connection {i}")
                for i in range(5)  # 5 one-away groups
            ],
            llm_prompt_template="standard",
        )

        session_id = "test-large-context-timing"
        start_time = time.time()

        recommendation = await llm_service.generate_recommendation(
            session_id=session_id, context=large_context, llm_model="gpt-4"
        )

        elapsed_time = time.time() - start_time

        # Even with large context, should be under 2 seconds
        assert elapsed_time < 2.0, f"Large context recommendation took {elapsed_time:.2f}s, exceeds 2s limit"

        # Verify recommendation was generated
        assert recommendation is not None
        assert len(recommendation.recommended_words) == 4

    @pytest.mark.asyncio
    async def test_timing_consistency(self, llm_service: LLMService, sample_context: AIRecommendationContext):
        """Test that recommendation timing is consistent across multiple calls."""
        session_id = "test-timing-consistency"
        elapsed_times = []

        # Generate 10 recommendations to test consistency
        for i in range(10):
            start_time = time.time()
            await llm_service.generate_recommendation(
                session_id=f"{session_id}-{i}", context=sample_context, llm_model="gpt-4"
            )
            elapsed_times.append(time.time() - start_time)

        # All should be under 2 seconds
        for i, elapsed in enumerate(elapsed_times):
            assert elapsed < 2.0, f"Recommendation {i} took {elapsed:.2f}s, exceeds 2s limit"

        # Check for reasonable variance (no extreme outliers)
        avg_time = sum(elapsed_times) / len(elapsed_times)
        max_time = max(elapsed_times)
        min_time = min(elapsed_times)

        # Max shouldn't be more than 3x the minimum (reasonable variance)
        assert max_time <= min_time * 3, f"Timing variance too high: min={min_time:.2f}s, max={max_time:.2f}s"

    @pytest.mark.asyncio
    async def test_processing_time_tracking(self, llm_service: LLMService, sample_context: AIRecommendationContext):
        """Test that processing time is accurately tracked in recommendation object."""
        session_id = "test-processing-time-tracking"

        recommendation = await llm_service.generate_recommendation(
            session_id=session_id, context=sample_context, llm_model="gpt-4"
        )

        # Processing time should be reasonable (in milliseconds)
        assert recommendation.processing_time_ms > 0
        assert recommendation.processing_time_ms < 2000  # Under 2 seconds in ms

        # Should be a reasonable approximation of actual time
        # (Allow some margin for overhead, but not too much)
        assert recommendation.processing_time_ms >= 50  # At least some processing time


class TestRecommendationMemoryUsage:
    """Test memory usage during recommendation generation."""

    @pytest.fixture
    def sample_context(self) -> AIRecommendationContext:
        """Create sample AI context for testing."""
        return AIRecommendationContext(
            session_id="test-session-123",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
            llm_prompt_template="standard",
        )

    @pytest.mark.asyncio
    async def test_memory_efficiency_multiple_recommendations(self, sample_context: AIRecommendationContext):
        """Test that multiple recommendations don't cause memory leaks."""
        llm_service = LLMService()

        # Generate many recommendations to test for memory leaks
        for i in range(50):
            recommendation = await llm_service.generate_recommendation(
                session_id=f"memory-test-{i}", context=sample_context, llm_model="gpt-4"
            )

            # Verify each recommendation is generated correctly
            assert recommendation is not None
            assert len(recommendation.recommended_words) == 4

        # If we get here without memory issues, the test passes
        # In a real implementation, we might use memory profiling tools
        # to verify actual memory usage patterns

    @pytest.mark.asyncio
    async def test_context_cleanup(self, sample_context: AIRecommendationContext):
        """Test that contexts are properly cleaned up after processing."""
        llm_service = LLMService()

        # Generate recommendation
        recommendation = await llm_service.generate_recommendation(
            session_id="cleanup-test", context=sample_context, llm_model="gpt-4"
        )

        # Verify recommendation was generated
        assert recommendation is not None

        # Context should not be modified (immutable behavior)
        assert len(sample_context.remaining_words) == 4
        assert sample_context.solved_groups == []
        assert sample_context.incorrect_groups == []
        assert sample_context.one_away_groups == []


class TestPerformanceEdgeCases:
    """Test performance in edge case scenarios."""

    @pytest.mark.asyncio
    async def test_minimal_context_timing(self):
        """Test timing with minimal context (exactly 4 words)."""
        minimal_context = AIRecommendationContext(
            session_id="minimal-context-session",
            remaining_words=["word1", "word2", "word3", "word4"],
            solved_groups=[],
            incorrect_groups=[],
            one_away_groups=[],
            llm_prompt_template="standard",
        )

        llm_service = LLMService()
        start_time = time.time()

        recommendation = await llm_service.generate_recommendation(
            session_id="minimal-context-test", context=minimal_context, llm_model="gpt-4"
        )

        elapsed_time = time.time() - start_time

        # Should still be under 2 seconds even with minimal context
        assert elapsed_time < 2.0, f"Minimal context took {elapsed_time:.2f}s, exceeds 2s limit"
        assert recommendation is not None

    @pytest.mark.asyncio
    async def test_maximum_context_timing(self):
        """Test timing with maximum realistic context."""
        # Maximum realistic context: 16 words, many previous attempts
        max_context = AIRecommendationContext(
            remaining_words=[f"remaining_{i}" for i in range(16)],
            solved_groups=[],  # Near end of game, all groups solved
            incorrect_groups=[[f"incorrect_{i}_{j}" for j in range(4)] for i in range(20)],  # Many failed attempts
            one_away_groups=[
                OneAwayGroup(words=[f"oneaway_{i}_{j}" for j in range(4)], explanation=f"Connection {i}")
                for i in range(10)  # Many one-away attempts
            ],
        )

        llm_service = LLMService()
        start_time = time.time()

        recommendation = await llm_service.generate_recommendation(
            session_id="maximum-context-test", context=max_context, llm_model="gpt-4"
        )

        elapsed_time = time.time() - start_time

        # Should still be under 2 seconds even with maximum context
        assert elapsed_time < 2.0, f"Maximum context took {elapsed_time:.2f}s, exceeds 2s limit"
        assert recommendation is not None
