"""
Contract tests for GET /api/v1/puzzles/{puzzle_id} endpoint.

This test validates the API contract for retrieving puzzle details.
These tests MUST FAIL until the actual endpoint is implemented.

Test Scenarios:
- Retrieve existing puzzle by valid UUID
- Handle non-existent puzzle IDs
- Validate response structure and field types
- Error response format validation
"""

import pytest
from fastapi.testclient import TestClient

# Import will fail until FastAPI app is created - this is expected for contract tests
try:
    from src.main import app

    client = TestClient(app)
except ImportError:
    # Contract test should fail when implementation doesn't exist
    client = None


class TestPuzzlesGetContract:
    """Contract tests for GET /api/v1/puzzles/{puzzle_id} endpoint."""

    def test_get_existing_puzzle_by_id(self):
        """Test retrieving an existing puzzle by valid UUID."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        # This would normally be a real puzzle ID from a previous upload
        # For contract testing, we use a valid UUID format
        test_puzzle_id = "12345678-1234-5678-9abc-123456789012"

        response = client.get(f"/api/v1/puzzles/{test_puzzle_id}")

        # Contract validation: Status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Contract validation: Response structure
        json_data = response.json()
        required_fields = ["id", "words", "uploaded_filename", "created_at"]
        for field in required_fields:
            assert field in json_data, f"Missing required field: {field}"

        # Contract validation: Field types and constraints
        assert isinstance(json_data["id"], str), "id must be string"
        assert json_data["id"] == test_puzzle_id, "returned id must match requested id"

        assert isinstance(json_data["words"], list), "words must be list"
        assert len(json_data["words"]) == 16, "words must have exactly 16 items"

        assert isinstance(json_data["uploaded_filename"], str), "uploaded_filename must be string"
        assert len(json_data["uploaded_filename"]) > 0, "uploaded_filename cannot be empty"

        assert isinstance(json_data["created_at"], str), "created_at must be string (ISO datetime)"

        # Contract validation: Optional user_id field
        if "user_id" in json_data:
            assert json_data["user_id"] is None or isinstance(json_data["user_id"], str)

        # Contract validation: Words array contents
        for word in json_data["words"]:
            assert isinstance(word, str), "Each word must be string"
            assert len(word) > 0, "Words cannot be empty"
            assert len(word) <= 20, "Words must be <= 20 characters"

        # Contract validation: All words are unique
        assert len(set(json_data["words"])) == 16, "All words must be unique"

    def test_get_puzzle_with_user_id(self):
        """Test retrieving puzzle that has associated user_id."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_puzzle_id = "87654321-4321-8765-4321-876543210987"

        response = client.get(f"/api/v1/puzzles/{test_puzzle_id}")

        assert response.status_code == 200
        json_data = response.json()

        # Should include user_id field (may be null or string)
        assert "user_id" in json_data
        if json_data["user_id"] is not None:
            assert isinstance(json_data["user_id"], str)
            assert len(json_data["user_id"]) > 0

    def test_get_puzzle_anonymous_session(self):
        """Test retrieving puzzle from anonymous session (no user_id)."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_puzzle_id = "11111111-2222-3333-4444-555555555555"

        response = client.get(f"/api/v1/puzzles/{test_puzzle_id}")

        assert response.status_code == 200
        json_data = response.json()

        # Anonymous puzzle should have null user_id
        assert "user_id" in json_data
        assert json_data["user_id"] is None

    def test_get_nonexistent_puzzle(self):
        """Test error response for non-existent puzzle ID."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        nonexistent_id = "99999999-9999-9999-9999-999999999999"

        response = client.get(f"/api/v1/puzzles/{nonexistent_id}")

        # Contract validation: Error response
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

        json_data = response.json()
        assert "error" in json_data, "Error response must have 'error' field"
        assert "message" in json_data, "Error response must have 'message' field"
        assert isinstance(json_data["error"], str), "error field must be string"
        assert isinstance(json_data["message"], str), "message field must be string"

        # Optional details field
        if "details" in json_data:
            assert json_data["details"] is None or isinstance(json_data["details"], dict)

    def test_get_puzzle_invalid_uuid_format(self):
        """Test error response for invalid UUID format."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        invalid_id = "not-a-valid-uuid"

        response = client.get(f"/api/v1/puzzles/{invalid_id}")

        # Should return 400 for invalid UUID format
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        json_data = response.json()
        assert "error" in json_data
        assert "message" in json_data
        assert isinstance(json_data["error"], str)
        assert isinstance(json_data["message"], str)

    def test_get_puzzle_empty_id(self):
        """Test error response for empty puzzle ID."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        # Empty ID should result in 404 (route not found) or 400
        response = client.get("/api/v1/puzzles/")

        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}"

    def test_get_puzzle_created_at_datetime_format(self):
        """Test that created_at field contains valid datetime format."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_puzzle_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

        response = client.get(f"/api/v1/puzzles/{test_puzzle_id}")

        assert response.status_code == 200
        json_data = response.json()

        created_at = json_data["created_at"]
        assert isinstance(created_at, str)
        # Basic ISO datetime format check (more rigorous validation in implementation tests)
        assert "T" in created_at or " " in created_at  # Should contain date/time separator
        assert len(created_at) >= 19  # Minimum length for "YYYY-MM-DD HH:MM:SS"

    def test_get_puzzle_filename_validation(self):
        """Test that uploaded_filename field contains valid filename."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_puzzle_id = "ffff1111-2222-3333-4444-555566667777"

        response = client.get(f"/api/v1/puzzles/{test_puzzle_id}")

        assert response.status_code == 200
        json_data = response.json()

        filename = json_data["uploaded_filename"]
        assert isinstance(filename, str)
        assert len(filename) > 0
        # Should have proper file extension
        assert filename.endswith((".txt", ".csv"))
        # Should not contain path separators (security check)
        assert "/" not in filename and "\\" not in filename

    def test_get_puzzle_words_constraints(self):
        """Test that words array meets all specified constraints."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_puzzle_id = "12ab34cd-56ef-78gh-90ij-klmnopqrstuv"

        response = client.get(f"/api/v1/puzzles/{test_puzzle_id}")

        assert response.status_code == 200
        json_data = response.json()

        words = json_data["words"]

        # Exactly 16 words
        assert len(words) == 16, f"Expected 16 words, got {len(words)}"

        # All words are unique (case-insensitive check would be in implementation)
        assert len(set(words)) == 16, "All words must be unique"

        # Each word meets constraints
        for i, word in enumerate(words):
            assert isinstance(word, str), f"Word at index {i} must be string"
            assert len(word) > 0, f"Word at index {i} cannot be empty"
            assert len(word) <= 20, f"Word at index {i} exceeds 20 character limit: {word}"
            # Should not have leading/trailing whitespace
            assert word.strip() == word, f"Word at index {i} has whitespace: '{word}'"
