"""Unit tests for context management logic."""

from datetime import datetime, timedelta
from unittest.mock import patch

from src.services.context_service import ContextService
from src.models.session import Session


class TestContextService:
    """Test cases for ContextService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ContextService()

    def test_init(self):
        """Test ContextService initialization."""
        assert self.service._contexts == {}
        assert self.service._default_prompt_template is not None
        assert len(self.service._default_prompt_template) > 0

    def test_create_context_for_session(self):
        """Test creating context for a new session."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context = self.service.create_context_for_session(session)

        assert context.session_id == "session_1"
        assert context.remaining_words == ["apple", "banana", "cherry", "date"]
        assert context.solved_groups == []
        assert context.incorrect_groups == []
        assert context.one_away_groups == []
        assert context.llm_prompt_template == self.service._default_prompt_template

        # Should be stored in service
        assert self.service._contexts["session_1"] == context

    def test_create_context_for_session_with_custom_words(self):
        """Test creating context with custom initial words."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        custom_words = ["cat", "dog", "bird", "fish"]
        context = self.service.create_context_for_session(session, custom_words)

        assert context.remaining_words == custom_words
        # Should not modify the original custom_words list
        custom_words.append("extra")
        assert len(context.remaining_words) == 4

    def test_get_context_for_session_exists(self):
        """Test getting existing context for session."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        original_context = self.service.create_context_for_session(session)
        retrieved_context = self.service.get_context_for_session("session_1")

        assert retrieved_context == original_context

    def test_get_context_for_session_not_exists(self):
        """Test getting non-existent context for session."""
        context = self.service.get_context_for_session("nonexistent")

        assert context is None

    def test_update_context_with_solved_group(self):
        """Test updating context with a solved group."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date", "cat", "dog", "bird", "fish"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context = self.service.create_context_for_session(session)

        with patch("src.services.context_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)

            updated_context = self.service.update_context_with_solved_group(
                "session_1", ["apple", "banana", "cherry", "date"], "Types of fruit", "yellow"
            )

        assert updated_context is not None
        assert len(updated_context.solved_groups) == 1
        assert updated_context.solved_groups[0].words == ["apple", "banana", "cherry", "date"]
        assert updated_context.solved_groups[0].theme == "Types of fruit"
        assert updated_context.solved_groups[0].difficulty == "yellow"
        assert updated_context.solved_groups[0].is_solved is True
        assert updated_context.remaining_words == ["cat", "dog", "bird", "fish"]
        assert updated_context.created_at == datetime(2023, 1, 1, 12, 0, 0)

    def test_update_context_with_solved_group_session_not_found(self):
        """Test updating context with solved group for non-existent session."""
        updated_context = self.service.update_context_with_solved_group(
            "nonexistent", ["apple", "banana", "cherry", "date"], "Types of fruit"
        )

        assert updated_context is None

    def test_update_context_with_incorrect_group(self):
        """Test updating context with an incorrect group."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context = self.service.create_context_for_session(session)

        with patch("src.services.context_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)

            updated_context = self.service.update_context_with_incorrect_group(
                "session_1", ["apple", "cat", "cherry", "date"]
            )

        assert updated_context is not None
        assert len(updated_context.incorrect_groups) == 1
        assert updated_context.incorrect_groups[0] == ["apple", "cat", "cherry", "date"]
        assert updated_context.remaining_words == ["apple", "banana", "cherry", "date"]  # Unchanged
        assert updated_context.created_at == datetime(2023, 1, 1, 12, 0, 0)

    def test_update_context_with_incorrect_group_duplicate(self):
        """Test updating context with duplicate incorrect group."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context = self.service.create_context_for_session(session)

        # Add same incorrect group twice
        incorrect_words = ["apple", "cat", "cherry", "date"]
        self.service.update_context_with_incorrect_group("session_1", incorrect_words)
        updated_context = self.service.update_context_with_incorrect_group("session_1", incorrect_words)

        # Should still only have one entry
        assert updated_context is not None
        assert len(updated_context.incorrect_groups) == 1

    def test_update_context_with_incorrect_group_session_not_found(self):
        """Test updating context with incorrect group for non-existent session."""
        updated_context = self.service.update_context_with_incorrect_group(
            "nonexistent", ["apple", "cat", "cherry", "date"]
        )

        assert updated_context is None

    def test_update_context_with_one_away_group(self):
        """Test updating context with a one-away group."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context = self.service.create_context_for_session(session)

        with patch("src.services.context_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)

            updated_context = self.service.update_context_with_one_away_group(
                "session_1",
                ["apple", "banana", "cherry", "grape"],
                "Types of fruit",
                "grape should be date",
            )

        assert updated_context is not None
        assert len(updated_context.one_away_groups) == 1
        assert updated_context.one_away_groups[0].attempted_words == ["apple", "banana", "cherry", "grape"]
        assert updated_context.one_away_groups[0].correct_connection == "Types of fruit"
        assert updated_context.one_away_groups[0].incorrect_word_hint == "grape should be date"
        assert updated_context.created_at == datetime(2023, 1, 1, 12, 0, 0)

    def test_update_context_with_one_away_group_minimal(self):
        """Test updating context with one-away group with minimal information."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context = self.service.create_context_for_session(session)

        updated_context = self.service.update_context_with_one_away_group(
            "session_1", ["apple", "banana", "cherry", "grape"]
        )

        assert updated_context is not None
        assert len(updated_context.one_away_groups) == 1
        assert updated_context.one_away_groups[0].attempted_words == ["apple", "banana", "cherry", "grape"]
        assert updated_context.one_away_groups[0].correct_connection is None
        assert updated_context.one_away_groups[0].incorrect_word_hint is None

    def test_update_context_with_one_away_group_duplicate(self):
        """Test updating context with duplicate one-away group."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context = self.service.create_context_for_session(session)

        # Add same one-away group twice
        attempted_words = ["apple", "banana", "cherry", "grape"]
        self.service.update_context_with_one_away_group("session_1", attempted_words)
        updated_context = self.service.update_context_with_one_away_group("session_1", attempted_words)

        # Should still only have one entry
        assert updated_context is not None
        assert len(updated_context.one_away_groups) == 1

    def test_update_context_with_one_away_group_session_not_found(self):
        """Test updating context with one-away group for non-existent session."""
        updated_context = self.service.update_context_with_one_away_group(
            "nonexistent", ["apple", "banana", "cherry", "grape"]
        )

        assert updated_context is None

    def test_generate_context_summary(self):
        """Test generating context summary."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date", "cat", "dog", "bird", "fish"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        self.service.create_context_for_session(session)

        summary = self.service.generate_context_summary("session_1")
        self.service.update_context_with_solved_group(
            "session_1", ["apple", "banana", "cherry", "date"], "Types of fruit", "yellow"
        )
        self.service.update_context_with_incorrect_group("session_1", ["cat", "dog", "bird", "snake"])
        self.service.update_context_with_one_away_group(
            "session_1", ["cat", "dog", "bird", "fish"], "Animals", "fish should be mammal"
        )

        summary = self.service.generate_context_summary("session_1")

        assert summary is not None
        assert summary["session_id"] == "session_1"
        assert summary["remaining_words_count"] == 4  # ["cat", "dog", "bird", "fish"]
        assert summary["remaining_words"] == ["cat", "dog", "bird", "fish"]
        assert summary["solved_groups_count"] == 1
        assert len(summary["solved_groups"]) == 1
        assert summary["solved_groups"][0]["words"] == ["apple", "banana", "cherry", "date"]
        assert summary["solved_groups"][0]["theme"] == "Types of fruit"
        assert summary["incorrect_attempts_count"] == 1
        assert summary["incorrect_groups"] == [["cat", "dog", "bird", "snake"]]
        assert summary["one_away_attempts_count"] == 1
        assert len(summary["one_away_groups"]) == 1
        assert summary["one_away_groups"][0]["attempted_words"] == ["cat", "dog", "bird", "fish"]
        assert "last_updated" in summary
        assert "prompt_template_length" in summary

    def test_generate_context_summary_session_not_found(self):
        """Test generating context summary for non-existent session."""
        summary = self.service.generate_context_summary("nonexistent")

        assert summary is None

    def test_update_prompt_template(self):
        """Test updating prompt template for a session."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context = self.service.create_context_for_session(session)
        original_template = context.llm_prompt_template

        new_template = "Custom prompt template for testing"

        with patch("src.services.context_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)

            result = self.service.update_prompt_template("session_1", new_template)

        assert result is True
        assert context.llm_prompt_template == new_template
        assert context.llm_prompt_template != original_template
        assert context.created_at == datetime(2023, 1, 1, 12, 0, 0)

    def test_update_prompt_template_session_not_found(self):
        """Test updating prompt template for non-existent session."""
        result = self.service.update_prompt_template("nonexistent", "new template")

        assert result is False

    def test_get_context_statistics_empty(self):
        """Test getting context statistics with no contexts."""
        stats = self.service.get_context_statistics()

        expected = {
            "total_contexts": 0,
            "active_sessions": 0,
            "average_solved_groups": 0.0,
            "average_incorrect_attempts": 0.0,
            "average_one_away_attempts": 0.0,
        }

        assert stats == expected

    def test_get_context_statistics_with_data(self):
        """Test getting context statistics with multiple contexts."""
        # Create multiple sessions with different states
        for i in range(3):
            session = Session(
                id=f"session_{i}",
                puzzle_id=f"puzzle_{i}",
                remaining_words=["apple", "banana", "cherry", "date"] if i < 2 else [],  # One completed
                solved_groups=[],
                llm_model="gpt-4",
            )

            self.service.create_context_for_session(session)

            # Add varying amounts of data
            if i >= 1:
                self.service.update_context_with_solved_group(
                    f"session_{i}", ["apple", "banana", "cherry", "date"], "Fruit"
                )
            if i >= 2:
                self.service.update_context_with_incorrect_group(f"session_{i}", ["cat", "dog", "bird", "fish"])
                self.service.update_context_with_one_away_group(f"session_{i}", ["red", "blue", "green", "purple"])

        stats = self.service.get_context_statistics()

        assert stats["total_contexts"] == 3
        assert stats["active_sessions"] == 2  # Two have remaining words
        assert stats["average_solved_groups"] == 2.0 / 3  # sessions 1 and 2 have 1 solved group each
        assert stats["average_incorrect_attempts"] == 1.0 / 3  # Only session 2 has incorrect attempts
        assert stats["average_one_away_attempts"] == 1.0 / 3  # Only session 2 has one-away attempts

    def test_cleanup_completed_contexts(self):
        """Test cleaning up completed and old contexts."""
        # Create contexts with different states and ages
        now = datetime.now()
        old_time = now - timedelta(hours=25)  # Older than 24 hours

        # Active session (has remaining words)
        active_session = Session(
            id="active_session",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )
        self.service.create_context_for_session(active_session)

        # Completed session (no remaining words)
        completed_session = Session(
            id="completed_session",
            puzzle_id="puzzle_2",
            remaining_words=[],
            solved_groups=[],
            llm_model="gpt-4",
        )
        self.service.create_context_for_session(completed_session)

        # Old session (older than max_age_hours)
        old_session = Session(
            id="old_session",
            puzzle_id="puzzle_3",
            remaining_words=["cat", "dog", "bird", "fish"],
            solved_groups=[],
            llm_model="gpt-4",
        )
        old_context = self.service.create_context_for_session(old_session)
        old_context.created_at = old_time

        # Should have 3 contexts before cleanup
        assert len(self.service._contexts) == 3

        cleaned_count = self.service.cleanup_completed_contexts(max_age_hours=24)

        # Should clean up completed and old contexts
        assert cleaned_count == 2
        assert len(self.service._contexts) == 1
        assert "active_session" in self.service._contexts
        assert "completed_session" not in self.service._contexts
        assert "old_session" not in self.service._contexts

    def test_reset_context(self):
        """Test resetting context to initial state."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date", "cat", "dog", "bird", "fish"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context = self.service.create_context_for_session(session)

        # Modify context state
        self.service.update_context_with_solved_group("session_1", ["apple", "banana", "cherry", "date"], "Fruit")
        self.service.update_context_with_incorrect_group("session_1", ["cat", "dog", "bird", "snake"])
        self.service.update_context_with_one_away_group("session_1", ["red", "blue", "green", "purple"])

        # Verify context has been modified
        assert len(context.solved_groups) == 1
        assert len(context.incorrect_groups) == 1
        assert len(context.one_away_groups) == 1
        assert len(context.remaining_words) == 4

        with patch("src.services.context_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)

            result = self.service.reset_context("session_1")

        assert result is True
        assert len(context.solved_groups) == 0
        assert len(context.incorrect_groups) == 0
        assert len(context.one_away_groups) == 0
        assert len(context.remaining_words) == 8  # All original words restored
        assert set(context.remaining_words) == {"apple", "banana", "cherry", "date", "cat", "dog", "bird", "fish"}
        assert context.created_at == datetime(2023, 1, 1, 12, 0, 0)

    def test_reset_context_session_not_found(self):
        """Test resetting context for non-existent session."""
        result = self.service.reset_context("nonexistent")

        assert result is False

    def test_delete_context(self):
        """Test deleting context for a session."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        self.service.create_context_for_session(session)
        assert "session_1" in self.service._contexts

        result = self.service.delete_context("session_1")

        assert result is True
        assert "session_1" not in self.service._contexts

    def test_delete_context_not_found(self):
        """Test deleting non-existent context."""
        result = self.service.delete_context("nonexistent")

        assert result is False

    def test_default_prompt_template(self):
        """Test that default prompt template is properly formatted."""
        template = self.service._get_default_prompt_template()

        assert isinstance(template, str)
        assert len(template) > 0
        assert "{solved_groups}" in template
        assert "{incorrect_groups}" in template
        assert "{one_away_groups}" in template
        assert "{remaining_words}" in template
        assert "WORDS:" in template
        assert "EXPLANATION:" in template

    def test_context_isolation(self):
        """Test that contexts for different sessions are isolated."""
        session1 = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        session2 = Session(
            id="session_2",
            puzzle_id="puzzle_2",
            remaining_words=["cat", "dog", "bird", "fish"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context1 = self.service.create_context_for_session(session1)
        context2 = self.service.create_context_for_session(session2)

        # Modify context1
        self.service.update_context_with_solved_group("session_1", ["apple", "banana", "cherry", "date"], "Fruit")

        # context2 should be unaffected
        assert len(context1.solved_groups) == 1
        assert len(context2.solved_groups) == 0
        assert context1.remaining_words != context2.remaining_words

    def test_update_preserves_other_data(self):
        """Test that updates preserve other context data."""
        session = Session(
            id="session_1",
            puzzle_id="puzzle_1",
            remaining_words=["apple", "banana", "cherry", "date", "cat", "dog", "bird", "fish"],
            solved_groups=[],
            llm_model="gpt-4",
        )

        context = self.service.create_context_for_session(session)

        # Add initial data
        self.service.update_context_with_incorrect_group("session_1", ["wrong1", "wrong2", "wrong3", "wrong4"])
        self.service.update_context_with_one_away_group("session_1", ["close1", "close2", "close3", "close4"])

        # Add solved group - should preserve other data
        self.service.update_context_with_solved_group("session_1", ["apple", "banana", "cherry", "date"], "Fruit")

        assert len(context.solved_groups) == 1
        assert len(context.incorrect_groups) == 1  # Preserved
        assert len(context.one_away_groups) == 1  # Preserved
        assert context.incorrect_groups[0] == ["wrong1", "wrong2", "wrong3", "wrong4"]
        assert context.one_away_groups[0].attempted_words == ["close1", "close2", "close3", "close4"]
