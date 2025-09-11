"""
Integration test for complete puzzle upload workflow.

This test validates the end-to-end puzzle upload functionality.
These tests MUST FAIL until the actual implementation is complete.

Test Scenarios:
- Complete file upload and puzzle creation workflow
- File validation and error handling
- Integration between upload, storage, and retrieval
"""

import pytest
from fastapi.testclient import TestClient
import io

# Import will fail until FastAPI app is created - this is expected for integration tests
try:
    from src.main import app

    client = TestClient(app)
except ImportError:
    # Integration test should fail when implementation doesn't exist
    client = None


class TestPuzzleUploadFlowIntegration:
    """Integration tests for complete puzzle upload workflow."""

    def test_complete_puzzle_upload_workflow(self):
        """Test complete workflow from file upload to puzzle retrieval."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")

        # Step 1: Upload a puzzle file
        puzzle_words = (
            "BASS,PIANO,GUITAR,DRUMS,FISH,SALMON,TROUT,TUNA,YELLOW,GREEN,BLUE,PURPLE,APPLE,BANANA,ORANGE,GRAPE"
        )
        file_data = io.BytesIO(puzzle_words.encode())
        files = {"file": ("test_puzzle.txt", file_data, "text/plain")}
        data = {"user_id": "integration-test-user"}

        upload_response = client.post("/api/v1/puzzles/upload", files=files, data=data)
        assert upload_response.status_code == 201

        upload_data = upload_response.json()
        puzzle_id = upload_data["id"]

        # Step 2: Retrieve the uploaded puzzle
        get_response = client.get(f"/api/v1/puzzles/{puzzle_id}")
        assert get_response.status_code == 200

        get_data = get_response.json()

        # Validate consistency between upload and retrieval
        assert get_data["id"] == puzzle_id
        assert get_data["uploaded_filename"] == "test_puzzle.txt"
        assert len(get_data["words"]) == 16
        assert set(get_data["words"]) == set(puzzle_words.split(","))

        # Step 3: Verify puzzle can be used for session creation
        session_request = {"puzzle_id": puzzle_id, "llm_model": "gpt-4"}

        session_response = client.post("/api/v1/sessions", json=session_request)
        assert session_response.status_code == 201

        session_data = session_response.json()
        assert session_data["puzzle_id"] == puzzle_id
        assert set(session_data["remaining_words"]) == set(puzzle_words.split(","))

    def test_puzzle_upload_error_handling_workflow(self):
        """Test error handling throughout the upload workflow."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")

        # Test invalid file content
        invalid_content = "ONLY,TWELVE,WORDS,HERE,NOT,ENOUGH,FOR,PUZZLE,GAME,RULES,NEED,SIXTEEN"
        file_data = io.BytesIO(invalid_content.encode())
        files = {"file": ("invalid.txt", file_data, "text/plain")}

        upload_response = client.post("/api/v1/puzzles/upload", files=files)
        assert upload_response.status_code == 400

        error_data = upload_response.json()
        assert "error" in error_data
        assert "message" in error_data

    def test_puzzle_upload_with_whitespace_handling(self):
        """Test that whitespace in uploaded words is handled correctly."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")

        # Words with various whitespace patterns
        puzzle_words = " WORD1 , WORD2,  WORD3,WORD4 ,WORD5,WORD6,WORD7,WORD8,WORD9,WORD10,WORD11,WORD12,WORD13,WORD14,WORD15,WORD16"
        file_data = io.BytesIO(puzzle_words.encode())
        files = {"file": ("whitespace_test.txt", file_data, "text/plain")}

        upload_response = client.post("/api/v1/puzzles/upload", files=files)
        assert upload_response.status_code == 201

        upload_data = upload_response.json()
        puzzle_id = upload_data["id"]

        # Verify words are properly trimmed
        get_response = client.get(f"/api/v1/puzzles/{puzzle_id}")
        assert get_response.status_code == 200

        get_data = get_response.json()
        for word in get_data["words"]:
            assert word.strip() == word, f"Word should not have whitespace: '{word}'"

    def test_puzzle_upload_duplicate_detection(self):
        """Test that duplicate words are properly detected and rejected."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")

        # Contains duplicate "WORD1"
        puzzle_words = (
            "WORD1,WORD1,WORD3,WORD4,WORD5,WORD6,WORD7,WORD8,WORD9,WORD10,WORD11,WORD12,WORD13,WORD14,WORD15,WORD16"
        )
        file_data = io.BytesIO(puzzle_words.encode())
        files = {"file": ("duplicates.txt", file_data, "text/plain")}

        upload_response = client.post("/api/v1/puzzles/upload", files=files)
        assert upload_response.status_code == 400

        error_data = upload_response.json()
        assert "error" in error_data
        assert "duplicate" in error_data["message"].lower()

    def test_puzzle_upload_csv_format_support(self):
        """Test that CSV file format is properly supported."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")

        puzzle_words = "A1,B2,C3,D4,E5,F6,G7,H8,I9,J10,K11,L12,M13,N14,O15,P16"
        file_data = io.BytesIO(puzzle_words.encode())
        files = {"file": ("puzzle.csv", file_data, "text/csv")}

        upload_response = client.post("/api/v1/puzzles/upload", files=files)
        assert upload_response.status_code == 201

        upload_data = upload_response.json()
        assert upload_data["uploaded_filename"] == "puzzle.csv"

        # Verify retrieval works
        puzzle_id = upload_data["id"]
        get_response = client.get(f"/api/v1/puzzles/{puzzle_id}")
        assert get_response.status_code == 200
