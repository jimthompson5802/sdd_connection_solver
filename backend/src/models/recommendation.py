"""Recommendation model for AI-generated group suggestions."""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class Recommendation(BaseModel):
    """Records an AI-generated group suggestion and user's evaluation.

    Args:
        id: Unique recommendation identifier
        session_id: Reference to user session
        recommended_words: The 4 words AI recommended to group together
        explanation: AI's reasoning for this grouping
        timestamp: When recommendation was generated
        user_evaluation: User's response ("correct", "incorrect", "one_away", None if pending)
        evaluation_timestamp: When user evaluated the recommendation
        llm_model: Which LLM model generated this (configuration parameter)
        processing_time_ms: Time taken to generate recommendation

    Returns:
        Recommendation instance with validation applied
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., min_length=1)
    recommended_words: List[str] = Field(..., min_items=4, max_items=4)
    explanation: str = Field(..., min_length=10, max_length=500)
    timestamp: datetime = Field(default_factory=datetime.now)
    user_evaluation: Optional[str] = Field(default=None, pattern="^(correct|incorrect|one_away)$|^$")
    evaluation_timestamp: Optional[datetime] = None
    llm_model: str = Field(..., min_length=1)
    processing_time_ms: int = Field(..., ge=0)

    @validator("recommended_words")
    def validate_recommended_words(cls, v: List[str]) -> List[str]:
        """Validate recommended words list.

        Args:
            v: List of words to validate

        Returns:
            Validated list of words

        Raises:
            ValueError: If validation fails
        """
        if len(v) != 4:
            raise ValueError("Must have exactly 4 recommended words")

        # Check for empty words
        if any(not word.strip() for word in v):
            raise ValueError("All recommended words must be non-empty")

        # Check for uniqueness (case-insensitive)
        lower_words = [word.lower().strip() for word in v]
        if len(set(lower_words)) != len(lower_words):
            raise ValueError("All recommended words must be unique")

        return [word.strip() for word in v]

    @validator("explanation")
    def validate_explanation(cls, v: str) -> str:
        """Validate explanation text.

        Args:
            v: Explanation to validate

        Returns:
            Validated explanation

        Raises:
            ValueError: If validation fails
        """
        if not v.strip():
            raise ValueError("Explanation cannot be empty")

        explanation = v.strip()
        if not (10 <= len(explanation) <= 500):
            raise ValueError("Explanation must be between 10 and 500 characters")

        return explanation

    @validator("user_evaluation")
    def validate_user_evaluation(cls, v: Optional[str]) -> Optional[str]:
        """Validate user evaluation value.

        Args:
            v: User evaluation to validate

        Returns:
            Validated user evaluation

        Raises:
            ValueError: If evaluation is invalid
        """
        if v is None:
            return v

        valid_evaluations = {"correct", "incorrect", "one_away"}
        if v not in valid_evaluations:
            raise ValueError(f"User evaluation must be one of: {', '.join(valid_evaluations)}")
        return v

    @validator("evaluation_timestamp")
    def validate_evaluation_timestamp(cls, v: Optional[datetime], values: dict) -> Optional[datetime]:
        """Validate evaluation timestamp consistency.

        Args:
            v: Evaluation timestamp to validate
            values: Other field values for cross-validation

        Returns:
            Validated evaluation timestamp

        Raises:
            ValueError: If timestamp is inconsistent with evaluation
        """
        user_evaluation = values.get("user_evaluation")

        if user_evaluation is not None and v is None:
            raise ValueError("evaluation_timestamp must be provided when user_evaluation is not None")

        if user_evaluation is None and v is not None:
            raise ValueError("evaluation_timestamp should be None when user_evaluation is None")

        return v

    @validator("processing_time_ms")
    def validate_processing_time(cls, v: int) -> int:
        """Validate processing time is non-negative.

        Args:
            v: Processing time to validate

        Returns:
            Validated processing time

        Raises:
            ValueError: If processing time is negative
        """
        if v < 0:
            raise ValueError("Processing time must be non-negative")
        return v

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        validate_assignment = True
