"""Puzzle service for file upload and word validation functionality."""

import csv
import io
from typing import List, Optional, Tuple

from ..models.puzzle import Puzzle


class PuzzleService:
    """Service for handling puzzle file uploads and word validation.

    Provides functionality to:
    - Parse uploaded text/CSV files
    - Validate word count and format
    - Create Puzzle instances from file content
    - Store puzzle data in memory (temporary implementation)
    """

    def __init__(self):
        """Initialize puzzle service with in-memory storage."""
        self._puzzles: dict[str, Puzzle] = {}

    def parse_uploaded_file(self, file_content: bytes, filename: str, user_id: Optional[str] = None) -> Puzzle:
        """Parse uploaded file content and create puzzle instance.

        Args:
            file_content: Raw bytes content of uploaded file
            filename: Original filename of uploaded file
            user_id: Optional user identifier

        Returns:
            Puzzle instance with validated words

        Raises:
            ValueError: If file parsing or validation fails
        """
        # Decode file content
        try:
            content_str = file_content.decode("utf-8").strip()
        except UnicodeDecodeError as e:
            raise ValueError(f"File encoding error: {e}")

        # Parse words from content
        words = self._parse_words_from_content(content_str, filename)

        # Validate word count
        if len(words) != 16:
            raise ValueError(f"Expected exactly 16 words, got {len(words)}")

        # Create and validate puzzle
        puzzle = Puzzle(words=words, uploaded_filename=filename, user_id=user_id)

        # Store puzzle
        self._puzzles[puzzle.id] = puzzle

        return puzzle

    def get_puzzle(self, puzzle_id: str) -> Optional[Puzzle]:
        """Retrieve puzzle by ID.

        Args:
            puzzle_id: Unique puzzle identifier

        Returns:
            Puzzle instance if found, None otherwise
        """
        return self._puzzles.get(puzzle_id)

    def validate_words(self, words: List[str]) -> Tuple[bool, List[str]]:
        """Validate a list of words for puzzle requirements.

        Args:
            words: List of words to validate

        Returns:
            Tuple of (is_valid, validation_errors)
        """
        errors = []

        # Check word count
        if len(words) != 16:
            errors.append(f"Must have exactly 16 words, got {len(words)}")

        # Check for empty words
        empty_indices = [i for i, word in enumerate(words) if not word.strip()]
        if empty_indices:
            errors.append(f"Empty words found at positions: {empty_indices}")

        # Check word length constraints
        for i, word in enumerate(words):
            word = word.strip()
            if len(word) > 20:
                errors.append(f"Word '{word}' at position {i} exceeds 20 character limit")
            if len(word) < 1:
                errors.append(f"Word at position {i} is too short (minimum 1 character)")

        # Check for duplicates
        word_counts = {}
        for i, word in enumerate(words):
            word_lower = word.strip().lower()
            if word_lower in word_counts:
                errors.append(f"Duplicate word '{word}' found at positions {word_counts[word_lower]} and {i}")
            else:
                word_counts[word_lower] = i

        return len(errors) == 0, errors

    def _parse_words_from_content(self, content: str, filename: str) -> List[str]:
        """Parse words from file content supporting multiple formats.

        Args:
            content: File content as string
            filename: Original filename for format detection

        Returns:
            List of parsed words

        Raises:
            ValueError: If parsing fails
        """
        # Try CSV format first (comma-separated)
        if "," in content:
            return self._parse_csv_content(content)

        # Try line-separated format
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        if len(lines) == 16:
            return lines

        # Try space-separated format
        words = content.split()
        if len(words) == 16:
            return words

        # Try tab-separated format
        if "\t" in content:
            words = content.split("\t")
            words = [word.strip() for word in words if word.strip()]
            if len(words) == 16:
                return words

        raise ValueError(
            f"Unable to parse 16 words from file '{filename}'. "
            f"Supported formats: CSV (comma-separated), line-separated, space-separated, or tab-separated."
        )

    def _parse_csv_content(self, content: str) -> List[str]:
        """Parse CSV content and extract words.

        Args:
            content: CSV content as string

        Returns:
            List of words from CSV

        Raises:
            ValueError: If CSV parsing fails
        """
        try:
            # Handle both single-row and multi-row CSV
            csv_reader = csv.reader(io.StringIO(content))
            words = []

            for row in csv_reader:
                words.extend([cell.strip() for cell in row if cell.strip()])

            return words

        except csv.Error as e:
            raise ValueError(f"CSV parsing error: {e}")

    def get_all_puzzles(self) -> List[Puzzle]:
        """Get all stored puzzles.

        Returns:
            List of all puzzle instances
        """
        return list(self._puzzles.values())

    def delete_puzzle(self, puzzle_id: str) -> bool:
        """Delete a puzzle by ID.

        Args:
            puzzle_id: Unique puzzle identifier

        Returns:
            True if puzzle was deleted, False if not found
        """
        if puzzle_id in self._puzzles:
            del self._puzzles[puzzle_id]
            return True
        return False
