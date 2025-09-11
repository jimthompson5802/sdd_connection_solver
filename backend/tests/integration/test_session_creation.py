"""
Integration test for session creation with LLM model selection.

This test validates the end-to-end session creation functionality.
These tests MUST FAIL until the actual implementation is complete.

Test Scenarios:
- Complete session creation workflow with different LLM models
- Integration between puzzle, session, and recommendation systems
- Session state management and consistency
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


class TestSessionCreationIntegration:
    """Integration tests for session creation with LLM model selection."""

    def test_complete_session_creation_workflow(self):
        """Test complete workflow from puzzle upload to session creation."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")

        # Step 1: Create a puzzle first
        puzzle_words = (
            "WORD1,WORD2,WORD3,WORD4,WORD5,WORD6,WORD7,WORD8," "WORD9,WORD10,WORD11,WORD12,WORD13,WORD14,WORD15,WORD16"
        )
        file_data = io.BytesIO(puzzle_words.encode())
        files = {"file": ("integration_test.txt", file_data, "text/plain")}

        upload_response = client.post("/api/v1/puzzles/upload", files=files)
        assert upload_response.status_code == 201
        puzzle_id = upload_response.json()["id"]

        # Step 2: Create session with different LLM models
        for llm_model in ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "claude-3-haiku"]:
            session_request = {"puzzle_id": puzzle_id, "llm_model": llm_model}

            session_response = client.post("/api/v1/sessions", json=session_request)
            assert session_response.status_code == 201

            session_data = session_response.json()
            session_id = session_data["id"]

            # Validate session configuration
            assert session_data["puzzle_id"] == puzzle_id
            assert session_data["llm_model_config"] == llm_model
            assert session_data["status"] == "active"
            assert session_data["can_request_recommendation"] is True

            # Step 3: Verify session can be retrieved
            get_response = client.get(f"/api/v1/sessions/{session_id}")
            assert get_response.status_code == 200

            get_data = get_response.json()
            assert get_data["id"] == session_id
            assert get_data["llm_model_config"] == llm_model

    def test_session_remaining_words_initialization(self):
        """Test that session properly initializes with all puzzle words."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")

        # Create puzzle with specific words
        words = [
            "APPLE",
            "BANANA",
            "CHERRY",
            "DATE",
            "ELDERBERRY",
            "FIG",
            "GRAPE",
            "HONEYDEW",
            "KIWI",
            "LEMON",
            "MANGO",
            "NECTARINE",
            "ORANGE",
            "PAPAYA",
            "QUINCE",
            "RASPBERRY",
        ]
        puzzle_content = ",".join(words)
        file_data = io.BytesIO(puzzle_content.encode())
        files = {"file": ("fruit_puzzle.txt", file_data, "text/plain")}

        upload_response = client.post("/api/v1/puzzles/upload", files=files)
        assert upload_response.status_code == 201
        puzzle_id = upload_response.json()["id"]

        # Create session
        session_request = {"puzzle_id": puzzle_id, "llm_model": "gpt-4"}
        session_response = client.post("/api/v1/sessions", json=session_request)
        assert session_response.status_code == 201

        session_data = session_response.json()

        # Verify all puzzle words are in remaining_words
        assert len(session_data["remaining_words"]) == 16
        assert set(session_data["remaining_words"]) == set(words)

    def test_session_multiple_users_same_puzzle(self):
        """Test that multiple users can create sessions for the same puzzle."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")

        # Create shared puzzle
        puzzle_words = "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P"
        file_data = io.BytesIO(puzzle_words.encode())
        files = {"file": ("shared_puzzle.txt", file_data, "text/plain")}
        upload_response = client.post("/api/v1/puzzles/upload", files=files)
        puzzle_id = upload_response.json()["id"]

        # Create multiple sessions for different users
        user_sessions = []
        for user_id in ["user1", "user2", "user3"]:
            session_request = {"puzzle_id": puzzle_id, "llm_model": "gpt-4", "user_id": user_id}

            session_response = client.post("/api/v1/sessions", json=session_request)
            assert session_response.status_code == 201

            session_data = session_response.json()
            user_sessions.append(session_data["id"])

        # Verify all sessions are independent
        assert len(set(user_sessions)) == 3, "All sessions should have unique IDs"

        # Each session should have the same initial state
        for session_id in user_sessions:
            get_response = client.get(f"/api/v1/sessions/{session_id}")
            session_data = get_response.json()

            assert session_data["puzzle_id"] == puzzle_id
            assert session_data["status"] == "active"
            assert len(session_data["remaining_words"]) == 16
