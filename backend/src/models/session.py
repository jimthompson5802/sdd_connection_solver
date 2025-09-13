"""Session model for tracking user's puzzle-solving session."""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic import field_validator
from pydantic import ConfigDict

from .recommendation import Recommendation
from .group import Group


class Session(BaseModel):
    """Tracks user's current puzzle-solving session and progress.

    Args:
        id: Unique session identifier
        puzzle_id: Reference to active puzzle
        start_time: Session start timestamp
        last_activity: Most recent user action
        status: Current session state ("active", "completed", "failed", "abandoned")
        solved_groups_count: Number of groups correctly identified (0-4)
        remaining_words: Words still available for recommendations
        incorrect_evaluation_count: Number of incorrect evaluations made (max 4)
        recommendation_history: All recommendations made in this session
        solved_groups: List of solved groups with themes and difficulties
        llm_model_config: Configured LLM model for this session
        pending_recommendation_id: ID of current unevaluated recommendation

    Returns:
        Session instance with validation applied
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    puzzle_id: str = Field(..., min_length=1)
    start_time: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="active")
    solved_groups_count: int = Field(default=0, ge=0, le=4)
    remaining_words: List[str] = Field(..., min_length=0, max_length=16)
    incorrect_evaluation_count: int = Field(default=0, ge=0, le=4)
    recommendation_history: List[Recommendation] = Field(default_factory=list)
    solved_groups: List[Group] = Field(default_factory=list)
    llm_model_config: str = Field(..., min_length=1)
    pending_recommendation_id: Optional[str] = None

    @field_validator("status")
    def validate_status(cls, v: str) -> str:
        """Validate session status.

        Args:
            v: Status to validate

        Returns:
            Validated status

        Raises:
            ValueError: If status is invalid
        """
        valid_statuses = {"active", "completed", "failed", "abandoned"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @field_validator("solved_groups_count")
    def validate_solved_groups_count(cls, v: int) -> int:
        """Validate solved groups count.

        Args:
            v: Count to validate

        Returns:
            Validated count

        Raises:
            ValueError: If count is out of range
        """
        if not (0 <= v <= 4):
            raise ValueError("Solved groups count must be between 0 and 4")
        return v

    @field_validator("remaining_words")
    def validate_remaining_words(cls, v: List[str], info) -> List[str]:
        """Validate remaining words consistency.

        Args:
            v: List of remaining words to validate
            values: Other field values for cross-validation

        Returns:
            Validated list of remaining words

        Raises:
            ValueError: If validation fails
        """
        # Validate count consistency with solved groups first
        solved_groups_count = info.data.get("solved_groups_count", 0)
        expected_remaining = 16 - (solved_groups_count * 4)

        # If puzzle is completed (expected_remaining = 0), allow empty list
        if expected_remaining == 0:
            if v:
                raise ValueError(
                    f"Remaining words should be empty when puzzle is completed "
                    f"(solved_groups_count={solved_groups_count})"
                )
            return v  # Return empty list for completed puzzles

        # For incomplete puzzles, remaining words cannot be empty
        if not v:
            raise ValueError("Remaining words cannot be empty for incomplete puzzles")

        # Check for empty words
        if any(not word.strip() for word in v):
            raise ValueError("All remaining words must be non-empty")

        # Check for uniqueness (case-insensitive)
        lower_words = [word.lower().strip() for word in v]
        if len(set(lower_words)) != len(lower_words):
            raise ValueError("All remaining words must be unique")

        # Validate count consistency
        if len(v) != expected_remaining:
            raise ValueError(
                f"Remaining words count ({len(v)}) doesn't match expected "
                f"({expected_remaining}) based on solved groups ({solved_groups_count})"
            )

        return [word.strip() for word in v]

    @field_validator("incorrect_evaluation_count")
    def validate_incorrect_evaluation_count(cls, v: int) -> int:
        """Validate incorrect evaluation count.

        Args:
            v: Count to validate

        Returns:
            Validated count

        Raises:
            ValueError: If count is out of range
        """
        if not (0 <= v <= 4):
            raise ValueError("Incorrect evaluation count must be between 0 and 4")
        return v

    @field_validator("recommendation_history")
    def validate_recommendation_history(cls, v: List[Recommendation]) -> List[Recommendation]:
        """Validate recommendation history is chronologically ordered.

        Args:
            v: List of recommendations to validate

        Returns:
            Validated list of recommendations

        Raises:
            ValueError: If recommendations are not chronologically ordered
        """
        if len(v) <= 1:
            return v

        # Check chronological order
        for i in range(1, len(v)):
            if v[i].timestamp < v[i - 1].timestamp:
                raise ValueError("Recommendation history must be chronologically ordered")

        return v

    @field_validator("last_activity")
    def validate_last_activity(cls, v: datetime, info) -> datetime:
        """Validate last activity is after start time.

        Args:
            v: Last activity timestamp to validate
            values: Other field values for cross-validation

        Returns:
            Validated timestamp

        Raises:
            ValueError: If last activity is before start time
        """
        start_time = info.data.get("start_time")
        if start_time and v < start_time:
            raise ValueError("Last activity cannot be before start time")
        return v

    def can_request_recommendation(self) -> bool:
        """Check if session can accept new recommendations.

        Returns:
            True if session can accept new recommendations, False otherwise
        """
        # Can't request if session is not active
        if self.status != "active":
            return False

        # Can't request if there's a pending recommendation
        if self.pending_recommendation_id is not None:
            return False

        # only pending_recommendation_id should block new requests

        # Can't request if too many incorrect evaluations
        if self.incorrect_evaluation_count >= 4:
            return False

        # Can't request if puzzle is already solved
        if self.solved_groups_count >= 4:
            return False

        # Can't request if not enough remaining words
        if len(self.remaining_words) < 4:
            return False

        return True

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()}, validate_assignment=True)
