"""Group model for a set of 4 related words with common theme."""

from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic import field_validator
from pydantic import ConfigDict


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
    words: List[str] = Field(..., min_length=4, max_length=4)
    is_solved: bool = Field(default=False)
    difficulty: str = Field(..., min_length=1, max_length=20)
    position: Optional[int] = Field(default=None)

    @field_validator("theme")
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
            raise ValueError("Group must have exactly 4 words")

        # Check for empty words
        if any(not word.strip() for word in v):
            raise ValueError("All words must be non-empty")

        # Check for uniqueness (case-insensitive)
        lower_words = [word.lower().strip() for word in v]
        if len(set(lower_words)) != len(lower_words):
            raise ValueError("All words in group must be unique")

        return [word.strip() for word in v]

    # difficulty is free-form (e.g., tests use values like 'medium'); keep length checks only

    model_config = ConfigDict(validate_assignment=True)
