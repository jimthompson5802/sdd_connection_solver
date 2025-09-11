"""Group model for a set of 4 related words with common theme."""

from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class Group(BaseModel):
    """A set of 4 related words with common theme/connection (hidden solution).

    Args:
        id: Unique group identifier
        theme: The connection description (e.g., "Types of Fish", "Musical Instruments")
        words: Exactly 4 words in this group (word texts)
        is_solved: Whether user has correctly identified this group
        difficulty: Group difficulty level ("yellow", "green", "blue", "purple")

    Returns:
        Group instance with validation applied
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    theme: str = Field(..., min_length=3, max_length=50)
    words: List[str] = Field(..., min_items=4, max_items=4)
    is_solved: bool = Field(default=False)
    difficulty: str = Field(..., pattern="^(yellow|green|blue|purple)$")

    @validator("theme")
    def validate_theme(cls, v: str) -> str:
        """Validate theme description.

        Args:
            v: Theme to validate

        Returns:
            Validated theme

        Raises:
            ValueError: If validation fails
        """
        if not v.strip():
            raise ValueError("Theme cannot be empty")

        theme = v.strip()
        if not (3 <= len(theme) <= 50):
            raise ValueError("Theme must be between 3 and 50 characters")

        return theme

    @validator("words")
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
            raise ValueError("Group must have exactly 4 words")

        # Check for empty words
        if any(not word.strip() for word in v):
            raise ValueError("All words must be non-empty")

        # Check for uniqueness (case-insensitive)
        lower_words = [word.lower().strip() for word in v]
        if len(set(lower_words)) != len(lower_words):
            raise ValueError("All words in group must be unique")

        return [word.strip() for word in v]

    @validator("difficulty")
    def validate_difficulty(cls, v: str) -> str:
        """Validate difficulty level.

        Args:
            v: Difficulty level to validate

        Returns:
            Validated difficulty level

        Raises:
            ValueError: If difficulty is invalid
        """
        valid_difficulties = {"yellow", "green", "blue", "purple"}
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(valid_difficulties)}")
        return v

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
