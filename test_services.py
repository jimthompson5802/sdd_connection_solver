"""Simple tests to verify the services are working correctly."""

import pytest
from src.services.puzzle_service import PuzzleService
from src.services.session_service import SessionService
from src.services.llm_service import LLMService
from src.services.evaluation_service import EvaluationService
from src.services.context_service import ContextService


def test_puzzle_service_basic():
    """Test basic puzzle service functionality."""
    service = PuzzleService()

    # Test CSV content parsing
    csv_content = "BASS,PIANO,GUITAR,DRUMS,FISH,SALMON,TROUT,TUNA,YELLOW,GREEN,BLUE,PURPLE,APPLE,BANANA,ORANGE,GRAPE"
    content_bytes = csv_content.encode("utf-8")

    puzzle = service.parse_uploaded_file(content_bytes, "test.csv")

    assert len(puzzle.words) == 16
    assert puzzle.uploaded_filename == "test.csv"
    assert "BASS" in puzzle.words

    # Test retrieval
    retrieved = service.get_puzzle(puzzle.id)
    assert retrieved is not None
    assert retrieved.id == puzzle.id


def test_session_service_basic():
    """Test basic session service functionality."""
    service = SessionService()

    # Create session
    puzzle_id = "test-puzzle-123"
    llm_model = "gpt-4"
    session = service.create_session(puzzle_id, llm_model)

    assert session.puzzle_id == puzzle_id
    assert session.llm_model_config == llm_model
    assert session.status == "active"
    assert len(session.remaining_words) == 16  # Default placeholder words

    # Test retrieval
    retrieved = service.get_session(session.id)
    assert retrieved is not None
    assert retrieved.id == session.id

    # Test solving a group (use actual words from the session)
    test_words = session.remaining_words[:4]  # Take first 4 words
    success = service.solve_group(session.id, test_words)
    assert success is True

    updated_session = service.get_session(session.id)
    assert updated_session.solved_groups_count == 1
    assert len(updated_session.remaining_words) == 12


@pytest.mark.asyncio
async def test_llm_service_basic():
    """Test basic LLM service functionality."""
    from src.models.ai_context import AIRecommendationContext

    service = LLMService()

    # Create context
    context = AIRecommendationContext(
        session_id="test-session",
        remaining_words=["BASS", "PIANO", "GUITAR", "DRUMS"],
        llm_prompt_template="test template",
    )

    # Generate recommendation
    recommendation = await service.generate_recommendation(
        session_id="test-session", context=context, llm_model="gpt-4"
    )

    assert recommendation.session_id == "test-session"
    assert len(recommendation.recommended_words) == 4
    assert recommendation.llm_model == "gpt-4"
    assert recommendation.processing_time_ms > 0


def test_evaluation_service_basic():
    """Test basic evaluation service functionality."""
    from src.models.recommendation import Recommendation

    service = EvaluationService()

    # Create recommendation
    recommendation = Recommendation(
        session_id="test-session",
        recommended_words=["BASS", "PIANO", "GUITAR", "DRUMS"],
        explanation="Musical instruments",
        llm_model="gpt-4",
        processing_time_ms=1000,
    )

    # Evaluate as correct
    updated_rec, updated_context = service.evaluate_recommendation(
        recommendation, "correct"
    )

    assert updated_rec.user_evaluation == "correct"
    assert updated_rec.evaluation_timestamp is not None

    # Get statistics
    stats = service.get_evaluation_statistics("test-session")
    assert stats["total_evaluations"] == 1
    assert stats["correct_count"] == 1
    assert stats["accuracy_rate"] == 1.0


def test_context_service_basic():
    """Test basic context service functionality."""
    from src.models.session import Session

    service = ContextService()

    # Create session with proper 16 words (required by validation)
    initial_words = [
        "BASS",
        "PIANO",
        "GUITAR",
        "DRUMS",
        "FISH",
        "SALMON",
        "TROUT",
        "TUNA",
        "YELLOW",
        "GREEN",
        "BLUE",
        "PURPLE",
        "APPLE",
        "BANANA",
        "ORANGE",
        "GRAPE",
    ]
    session = Session(
        puzzle_id="test-puzzle", llm_model_config="gpt-4", remaining_words=initial_words
    )

    # Create context
    context = service.create_context_for_session(session)

    assert context.session_id == session.id
    assert len(context.remaining_words) == 16
    assert len(context.solved_groups) == 0

    # Test solving a group
    updated_context = service.update_context_with_solved_group(
        session.id, ["BASS", "PIANO", "GUITAR", "DRUMS"], "Musical instruments"
    )

    assert updated_context is not None
    assert len(updated_context.solved_groups) == 1
    assert len(updated_context.remaining_words) == 12

    # Get summary
    summary = service.generate_context_summary(session.id)
    assert summary is not None
    assert summary["solved_groups_count"] == 1
    assert summary["remaining_words_count"] == 12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
