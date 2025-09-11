"""Puzzle model for NYT Connections puzzle instance."""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class Puzzle(BaseModel):
    """Represents a complete NYT Connections puzzle instance created from user file upload.

    Args:
        id: Unique puzzle identifier (UUID)
        words: Exactly 16 user-uploaded words (from CSV file)
        uploaded_filename: Original filename of uploaded text file
        created_at: Puzzle creation timestamp
        user_id: User identifier (None for anonymous sessions)

    Returns:
        Puzzle instance with validation applied
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    words: List[str] = Field(..., min_items=16, max_items=16)
    uploaded_filename: str = Field(..., min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None

    @validator("words")
    def validate_words(cls, v: List[str]) -> List[str]:
        """Validate words list meets requirements.

        Args:
            v: List of words to validate

        Returns:
            Validated list of words

        Raises:
            ValueError: If validation fails
        """
        if len(v) != 16:
            raise ValueError("Must have exactly 16 words")

        # Check for empty strings
        if any(not word.strip() for word in v):
            raise ValueError("All words must be non-empty strings")

        # Check word length
        for word in v:
            if len(word.strip()) > 20:
                raise ValueError(f"Word '{word}' exceeds 20 character limit")

        # Check for uniqueness (case-insensitive)
        lower_words = [word.lower().strip() for word in v]
        if len(set(lower_words)) != len(lower_words):
            raise ValueError("All words must be unique (case-insensitive)")

        return [word.strip() for word in v]

    @validator("uploaded_filename")
    def validate_filename(cls, v: str) -> str:
        """Validate uploaded filename has valid extension.

        Args:
            v: Filename to validate

        Returns:
            Validated filename

        Raises:
            ValueError: If filename is invalid
        """
        if not v.strip():
            raise ValueError("Filename cannot be empty")

        filename = v.strip().lower()
        if not (filename.endswith(".txt") or filename.endswith(".csv")):
            raise ValueError("Filename must have .txt or .csv extension")

        return v.strip()

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
