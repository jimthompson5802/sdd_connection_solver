"""FastAPI endpoints for health checks."""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..services.llm_service import LLMService
from ..storage.session_storage import InMemoryStorage


router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint.

    Returns:
        Dict containing service status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "nyt-connections-puzzle-assistant",
        "version": "1.0.0",
    }


@router.get("/health/db")
async def health_check_database() -> Dict[str, Any]:
    """Database health check endpoint.

    Returns:
        Dict containing database status and connection info

    Raises:
        HTTPException: If database connection fails
    """
    try:
        # Initialize storage and test basic operations
        storage = InMemoryStorage()

        # Test storage connectivity by attempting a basic operation
        # Since it's in-memory, we'll test initialization and basic functionality
        test_start = datetime.utcnow()

        # Test creating and retrieving a test session to verify storage works
        from ..models.session import Session
        from ..models.puzzle import Puzzle

        # Create a minimal test puzzle and session
        test_puzzle = Puzzle(
            puzzle_id="health-check-test",
            words=["test", "check", "health", "status"] * 4,  # 16 words as required
            created_at=test_start,
        )

        test_session = Session(session_id="health-check-session", puzzle_id="health-check-test", created_at=test_start)

        # Test storage operations
        await storage.create_puzzle(test_puzzle)
        await storage.create_session(test_session)

        # Verify retrieval works
        retrieved_puzzle = await storage.get_puzzle("health-check-test")
        retrieved_session = await storage.get_session("health-check-session")

        if not retrieved_puzzle or not retrieved_session:
            raise Exception("Storage retrieval test failed")

        # Clean up test data
        await storage.delete_session("health-check-session")
        # Note: In-memory storage doesn't have explicit puzzle deletion, but that's ok for health check

        response_time = (datetime.utcnow() - test_start).total_seconds()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database_type": "in_memory",
            "response_time_seconds": response_time,
            "operations_tested": ["store_puzzle", "store_session", "get_puzzle", "get_session", "delete_session"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database_type": "in_memory",
                "error": str(e),
                "message": "Database health check failed",
            },
        )


@router.get("/health/llm")
async def health_check_llm() -> Dict[str, Any]:
    """LLM service health check endpoint.

    Returns:
        Dict containing LLM service status and response info

    Raises:
        HTTPException: If LLM service is unavailable
    """
    try:
        # Initialize LLM service
        llm_service = LLMService()

        test_start = datetime.utcnow()

        # Test LLM service with a simple health check request
        # Since the current LLM service is in mock mode, we'll test its basic functionality
        from ..models.ai_context import AIRecommendationContext

        # Create a minimal test context
        test_context = AIRecommendationContext(
            context_id="health-check-context",
            session_id="health-check-session",
            puzzle_id="health-check-puzzle",
            remaining_words=["test", "check", "health", "status"],
            previous_recommendations=[],
            incorrect_attempts=[],
            one_away_attempts=[],
            found_groups=[],
            created_at=test_start,
        )

        # Test LLM service basic functionality
        try:
            # Call the LLM service to generate a test recommendation
            recommendations = await llm_service.generate_recommendations(test_context, limit=1)

            if not recommendations or len(recommendations) == 0:
                raise Exception("LLM service returned no recommendations")

            response_time = (datetime.utcnow() - test_start).total_seconds()

            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "llm_service": "mock_mode" if llm_service._mock_mode else "live_mode",
                "response_time_seconds": response_time,
                "test_recommendations_count": len(recommendations),
                "available_models": (
                    list(llm_service._model_configs.keys()) if hasattr(llm_service, "_model_configs") else []
                ),
            }

        except Exception as service_error:
            raise Exception(f"LLM service test failed: {str(service_error)}")

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "llm_service": "unknown",
                "error": str(e),
                "message": "LLM service health check failed",
            },
        )
