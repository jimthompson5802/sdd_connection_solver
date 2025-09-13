"""OneAwayGroup model for groups marked as one-away."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from pydantic import field_validator
from pydantic import ConfigDict


class OneAwayGroup(BaseModel):
    """Stores information about a group marked as one-away (3/4 words correct, but unknown which).

    Args:
        words: The 4 words from the one-away recommendation
        explanation: Original explanation for why these words were grouped
        marked_at: When this was marked as one-away

    Returns:
        OneAwayGroup instance with validation applied
    """

    words: List[str] = Field(..., min_length=4, max_length=4)
    explanation: str = Field(..., min_length=10, max_length=500)
    marked_at: datetime = Field(default_factory=datetime.now)

    @field_validator("words")
    def validate_words(cls, v: List[str]) -> List[str]:
        """Validate words list.

        Args:
            v: List of words to validate

        Returns:
            Validated list of words

        Raises:
            ValueError: If validation fails
        """
        if len(v) != 4:
            raise ValueError("OneAwayGroup must have exactly 4 words")

        # Check for empty words
        if any(not word.strip() for word in v):
            raise ValueError("All words must be non-empty")

        # Check for uniqueness (case-insensitive)
        lower_words = [word.lower().strip() for word in v]
        if len(set(lower_words)) != len(lower_words):
            raise ValueError("All words in OneAwayGroup must be unique")

        return [word.strip() for word in v]

    @field_validator("explanation")
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

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()}, validate_assignment=True)
