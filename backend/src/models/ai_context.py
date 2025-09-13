"""AIRecommendationContext model for storing LLM context information."""

from datetime import datetime
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic import field_validator
from pydantic import ConfigDict

from .group import Group
from .one_away_group import OneAwayGroup


class AIRecommendationContext(BaseModel):
    """Stores context information used by LLM to generate recommendations.

    Args:
        id: Unique context identifier
        session_id: Reference to session this context belongs to
        remaining_words: Available words at time of recommendation
        incorrect_groups: Previously incorrect word combinations
        one_away_groups: Groups marked as one-away with partial connection info
        solved_groups: Successfully identified groups (for reference)
        llm_prompt_template: Template used for LLM prompting
        created_at: Context creation timestamp

    Returns:
        AIRecommendationContext instance with validation applied
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(default="")
    remaining_words: List[str] = Field(..., max_length=16)
    incorrect_groups: List[List[str]] = Field(default_factory=list)
    one_away_groups: List[OneAwayGroup] = Field(default_factory=list)
    solved_groups: List[Group] = Field(default_factory=list)
    llm_prompt_template: str = Field(default="default_template")
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("remaining_words")
    def validate_remaining_words(cls, v: List[str]) -> List[str]:
        """Validate remaining words list.

        Args:
            v: List of words to validate

        Returns:
            Validated list of words

        Raises:
            ValueError: If validation fails
        """
        if not (0 <= len(v) <= 16):
            raise ValueError("Remaining words must contain 0-16 words depending on game progress")

        # Allow empty list when game is completed
        if len(v) == 0:
            return v

        # Check for empty words
        if any(not word.strip() for word in v):
            raise ValueError("All remaining words must be non-empty")

        # Check for uniqueness (case-insensitive)
        lower_words = [word.lower().strip() for word in v]
        if len(set(lower_words)) != len(lower_words):
            raise ValueError("All remaining words must be unique")

        return [word.strip() for word in v]

    @field_validator("incorrect_groups")
    def validate_incorrect_groups(cls, v: List[List[str]]) -> List[List[str]]:
        """Validate incorrect groups list.

        Args:
            v: List of incorrect groups to validate

        Returns:
            Validated list of incorrect groups

        Raises:
            ValueError: If validation fails
        """
        for i, group in enumerate(v):
            if len(group) != 4:
                raise ValueError(f"Incorrect group {i} must contain exactly 4 words")

            # Check for empty words
            if any(not word.strip() for word in group):
                raise ValueError(f"All words in incorrect group {i} must be non-empty")

            # Check for uniqueness within group (case-insensitive)
            lower_words = [word.lower().strip() for word in group]
            if len(set(lower_words)) != len(lower_words):
                raise ValueError(f"All words in incorrect group {i} must be unique")

        # Clean up words
        return [[word.strip() for word in group] for group in v]

    @field_validator("llm_prompt_template")
    def validate_llm_prompt_template(cls, v: str) -> str:
        """Validate LLM prompt template.

        Args:
            v: Template to validate

        Returns:
            Validated template

        Raises:
            ValueError: If template is empty
        """
        if not v.strip():
            raise ValueError("LLM prompt template cannot be empty")
        return v.strip()

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()}, validate_assignment=True)
