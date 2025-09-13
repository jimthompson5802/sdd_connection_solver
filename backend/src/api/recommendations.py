"""FastAPI endpoints for AI recommendation operations."""

from fastapi import APIRouter, HTTPException
from uuid import UUID
from pydantic import BaseModel

from ..services.session_service import SessionService
from ..services.llm_service import LLMService
from ..services.evaluation_service import EvaluationService
from ..models.ai_context import AIRecommendationContext


router = APIRouter(prefix="/api/v1/sessions", tags=["AI Recommendations"])
session_service = SessionService()
llm_service = LLMService()
evaluation_service = EvaluationService()


class EvaluateRecommendationRequest(BaseModel):
    """Request model for evaluating a recommendation."""

    evaluation: str


@router.post("/{session_id}/recommendations", response_model=dict, status_code=201)
async def generate_recommendation(session_id: str):
    """Generate next AI recommendation for current puzzle state.

    Args:
        session_id: UUID of the session

    Returns:
        RecommendationResponse with new recommendation details

    Raises:
        HTTPException: If session state is invalid or pending recommendation exists
    """
    try:
        # Get session
        session = session_service.get_session(session_id)
        if session is None:
            raise HTTPException(
                status_code=400,
                detail={"error": "SESSION_NOT_FOUND", "message": f"Session with ID {session_id} not found"},
            )

        # Check if session can accept new recommendations
        if not session.can_request_recommendation():
            if session.pending_recommendation_id:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "PENDING_RECOMMENDATION_EXISTS",
                        "message": "Must evaluate pending recommendation before requesting new one",
                    },
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "INVALID_SESSION_STATE",
                        "message": "Session cannot accept new recommendations in current state",
                    },
                )

        # Create AI context for LLM
        ai_context = AIRecommendationContext(
            session_id=session_id,
            remaining_words=session.remaining_words,
            incorrect_groups=[],  # TODO: Extract from session history
            one_away_groups=[],  # TODO: Extract from session history
            solved_groups=session.solved_groups,
            llm_prompt_template="default_template",  # TODO: Use actual template
        )

        # Generate recommendation using LLM service
        recommendation = await llm_service.generate_recommendation(
            session_id=session_id, context=ai_context, llm_model=session.llm_model_config
        )

        # Add recommendation to session
        session_service.add_recommendation_to_session(session_id, recommendation)

        # Return response matching API schema
        return {
            "id": recommendation.id,
            "recommended_words": recommendation.recommended_words,
            "explanation": recommendation.explanation,
            "timestamp": recommendation.timestamp.isoformat(),
            "user_evaluation": recommendation.user_evaluation,
            "evaluation_timestamp": (
                recommendation.evaluation_timestamp.isoformat() if recommendation.evaluation_timestamp else None
            ),
            "llm_model": recommendation.llm_model,
            "processing_time_ms": recommendation.processing_time_ms,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500, detail={"error": "INTERNAL_ERROR", "message": "Failed to generate recommendation"}
        )


@router.get("/{session_id}/recommendations", response_model=dict)
async def get_current_recommendation(session_id: str):
    """Get current pending recommendation.

    Args:
        session_id: UUID of the session

    Returns:
        RecommendationResponse with current recommendation details

    Raises:
        HTTPException: If no pending recommendation exists
    """
    try:
        # Validate UUID format for session — return 400 for malformed UUIDs
        try:
            UUID(session_id)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_SESSION_UUID", "message": f"Session ID {session_id} is not a valid UUID"},
            )

        # Get session
        session = session_service.get_session(session_id)
        if session is None:
            raise HTTPException(
                status_code=404,
                detail={"error": "SESSION_NOT_FOUND", "message": f"Session with ID {session_id} not found"},
            )

        # If session is not active, treat as having no pending recommendation
        if getattr(session, "status", "active") != "active":
            raise HTTPException(
                status_code=404,
                detail={"error": "NO_PENDING_RECOMMENDATION", "message": "No pending recommendation found for session"},
            )

        # Get current recommendation from session history
        if not session.recommendation_history:
            raise HTTPException(
                status_code=404,
                detail={"error": "NO_PENDING_RECOMMENDATION", "message": "No pending recommendation found for session"},
            )

        # Get most recent recommendation that hasn't been evaluated
        recommendation = None
        for rec in reversed(session.recommendation_history):
            if rec.user_evaluation is None:
                recommendation = rec
                break

        if recommendation is None:
            raise HTTPException(
                status_code=404,
                detail={"error": "NO_PENDING_RECOMMENDATION", "message": "No pending recommendation found for session"},
            )

        # Return response matching API schema
        return {
            "id": recommendation.id,
            "recommended_words": recommendation.recommended_words,
            "explanation": recommendation.explanation,
            "timestamp": recommendation.timestamp.isoformat(),
            "user_evaluation": recommendation.user_evaluation,
            "evaluation_timestamp": (
                recommendation.evaluation_timestamp.isoformat() if recommendation.evaluation_timestamp else None
            ),
            "llm_model": recommendation.llm_model,
            "processing_time_ms": recommendation.processing_time_ms,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500, detail={"error": "INTERNAL_ERROR", "message": "Failed to retrieve recommendation"}
        )


@router.post("/{session_id}/recommendations/{recommendation_id}/evaluate", response_model=dict)
async def evaluate_recommendation(session_id: str, recommendation_id: str, request: EvaluateRecommendationRequest):
    """Evaluate an AI recommendation as correct, incorrect, or one-away.

    Args:
        session_id: UUID of the session
        recommendation_id: UUID of the recommendation to evaluate
        request: Evaluation parameters

    Returns:
        EvaluationResponse with evaluation results and updated session state

    Raises:
        HTTPException: If recommendation not found or evaluation is invalid
    """
    try:
        # Validate UUID formats for session and recommendation — return 400 for malformed UUIDs
        try:
            UUID(session_id)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_SESSION_UUID", "message": f"Session ID {session_id} is not a valid UUID"},
            )

        try:
            UUID(recommendation_id)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_RECOMMENDATION_UUID",
                    "message": f"Recommendation ID {recommendation_id} is not a valid UUID",
                },
            )

        # Validate evaluation
        valid_evaluations = ["correct", "incorrect", "one_away"]
        if request.evaluation not in valid_evaluations:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_EVALUATION",
                    "message": f"Evaluation must be one of: {', '.join(valid_evaluations)}",
                },
            )

        # Find the recommendation to evaluate
        session = session_service.get_session(session_id)
        if session is None:
            raise HTTPException(
                status_code=404,
                detail={"error": "SESSION_NOT_FOUND", "message": f"Session with ID {session_id} not found"},
            )

        # Find recommendation by ID
        recommendation = None
        for rec in session.recommendation_history:
            if rec.id == recommendation_id:
                recommendation = rec
                break

        if recommendation is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "RECOMMENDATION_NOT_FOUND",
                    "message": f"Recommendation with ID {recommendation_id} not found",
                },
            )

        # Process evaluation using the available method
        updated_recommendation, _ = evaluation_service.evaluate_recommendation(
            recommendation=recommendation, evaluation=request.evaluation
        )

        # Update session based on evaluation result
        # For correct evaluations, we would typically solve the group
        # For now, just update the recommendation in session history

        # Get updated session state (in a real implementation, would be updated by the service)
        updated_session = session_service.get_session(session_id)
        if updated_session is None:
            raise HTTPException(
                status_code=500, detail={"error": "INTERNAL_ERROR", "message": "Failed to retrieve updated session"}
            )

        # Build response
        response = {
            "recommendation": {
                "id": updated_recommendation.id,
                "recommended_words": updated_recommendation.recommended_words,
                "explanation": updated_recommendation.explanation,
                "timestamp": updated_recommendation.timestamp.isoformat(),
                "user_evaluation": updated_recommendation.user_evaluation,
                "evaluation_timestamp": (
                    updated_recommendation.evaluation_timestamp.isoformat()
                    if updated_recommendation.evaluation_timestamp
                    else None
                ),
                "llm_model": updated_recommendation.llm_model,
                "processing_time_ms": updated_recommendation.processing_time_ms,
            },
            "session_status": updated_session.status,
            "next_action": "request_next_recommendation",
        }

        # For now, we don't have solved group detection implemented
        response["solved_group"] = None

        return response

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500, detail={"error": "INTERNAL_ERROR", "message": "Failed to evaluate recommendation"}
        )
