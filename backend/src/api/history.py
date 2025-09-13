"""FastAPI endpoints for session history operations."""

from fastapi import APIRouter, HTTPException

from ..services import session_service
import uuid


router = APIRouter(prefix="/api/v1/sessions", tags=["History"])


@router.get("/{session_id}/history", response_model=dict)
async def get_recommendation_history(session_id: str):
    """Get complete recommendation history for session.

    Args:
        session_id: UUID of the session

    Returns:
        RecommendationHistoryResponse with session history and summary

    Raises:
        HTTPException: If session is not found
    """
    try:
        # Validate session_id format (contract tests expect 400 for invalid UUIDs)
        try:
            uuid.UUID(session_id)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_SESSION_ID", "message": f"Session ID {session_id} is not a valid UUID"},
            )

        # Get session
        session = session_service.get_session(session_id)
        if session is None:
            raise HTTPException(
                status_code=404,
                detail={"error": "SESSION_NOT_FOUND", "message": f"Session with ID {session_id} not found"},
            )

        # Build recommendations list
        recommendations = []
        for rec in session.recommendation_history:
            recommendation_data = {
                "id": rec.id,
                "recommended_words": rec.recommended_words,
                "explanation": rec.explanation,
                "timestamp": rec.timestamp.isoformat(),
                "user_evaluation": rec.user_evaluation,
                "evaluation_timestamp": (rec.evaluation_timestamp.isoformat() if rec.evaluation_timestamp else None),
                "llm_model": rec.llm_model,
                "processing_time_ms": rec.processing_time_ms,
            }
            recommendations.append(recommendation_data)

        # Calculate session summary statistics
        total_recommendations = len(session.recommendation_history)
        correct_evaluations = sum(1 for rec in session.recommendation_history if rec.user_evaluation == "correct")
        incorrect_evaluations = sum(1 for rec in session.recommendation_history if rec.user_evaluation == "incorrect")
        one_away_evaluations = sum(1 for rec in session.recommendation_history if rec.user_evaluation == "one_away")

        # Calculate session duration
        session_duration_minutes = (session.last_activity - session.start_time).total_seconds() / 60.0

        # Build session summary
        session_summary = {
            "total_recommendations": total_recommendations,
            "correct_evaluations": correct_evaluations,
            "incorrect_evaluations": incorrect_evaluations,
            "one_away_evaluations": one_away_evaluations,
            "session_duration_minutes": round(session_duration_minutes, 2),
        }

        # Return response matching API schema
        return {"recommendations": recommendations, "session_summary": session_summary}

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500, detail={"error": "INTERNAL_ERROR", "message": "Failed to retrieve recommendation history"}
        )
