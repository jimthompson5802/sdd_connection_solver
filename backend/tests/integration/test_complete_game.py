"""
Integration test for complete game session from upload to completion.

This test validates the end-to-end game functionality.
These tests MUST FAIL until the actual implementation is complete.
"""

import pytest
from fastapi.testclient import TestClient

try:
    from src.main import app

    client = TestClient(app)
except ImportError:
    client = None


class TestCompleteGameIntegration:
    """Integration tests for complete game session."""

    def test_complete_game_session_workflow(self):
        """Test complete game from puzzle upload to session completion."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")
        # Upload puzzle, create session, retrieve session
        import io

        puzzle_words = (
            "BASS,PIANO,GUITAR,DRUMS,FISH,SALMON,TROUT,TUNA,YELLOW,GREEN,BLUE,PURPLE,APPLE,BANANA,ORANGE,GRAPE"
        )
        file_data = io.BytesIO(puzzle_words.encode())
        files = {"file": ("game_test.txt", file_data, "text/plain")}

        upload_response = client.post("/api/v1/puzzles/upload", files=files)
        assert upload_response.status_code == 201
        puzzle_id = upload_response.json()["id"]

        session_response = client.post("/api/v1/sessions", json={"puzzle_id": puzzle_id, "llm_model": "gpt-4"})
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]

        get_response = client.get(f"/api/v1/sessions/{session_id}")
        assert get_response.status_code == 200
        session_data = get_response.json()
        assert session_data["puzzle_id"] == puzzle_id
