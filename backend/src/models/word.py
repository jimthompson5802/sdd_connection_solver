"""Word model for individual puzzle elements."""

from pydantic import BaseModel, Field
from pydantic import field_validator
from pydantic import ConfigDict


class Word(BaseModel):
    """Individual puzzle element from uploaded file.

    Args:
        text: The word text as uploaded (e.g., "BASS", "PIANO")
        position: Position in uploaded file (0-15)
        is_solved: Whether this word is part of a correctly identified group

    Returns:
        Word instance with validation applied
    """

    text: str = Field(..., min_length=1, max_length=20)
    position: int = Field(..., ge=0, le=15)
    is_solved: bool = Field(default=False)

    @field_validator("text")
    def validate_text(cls, v: str) -> str:
        """Validate word text meets requirements.

        Args:
            v: Word text to validate

        Returns:
            Validated word text

        Raises:
            ValueError: If validation fails
        """
        if not v.strip():
            raise ValueError("Word text cannot be empty")

        text = v.strip()
        if len(text) > 20:
            raise ValueError("Word text must be 20 characters or less")

        # Allow alphanumeric plus common punctuation
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'-.,!?&")
        if not all(char in allowed_chars for char in text):
            raise ValueError("Word text contains invalid characters")

        return text

    @field_validator("position")
    def validate_position(cls, v: int) -> int:
        """Validate position is in valid range.

        Args:
            v: Position to validate

        Returns:
            Validated position

        Raises:
            ValueError: If position is out of range
        """
        if not (0 <= v <= 15):
            raise ValueError("Position must be between 0 and 15")
        return v

    model_config = ConfigDict(validate_assignment=True)
