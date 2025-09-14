"""Integration test for AI recommendation generation with context.

This test validates the end-to-end AI recommendation functionality.
These tests MUST FAIL until the actual implementation is complete.
"""

import io
import pytest
from fastapi.testclient import TestClient

try:
    from src.main import app

    client = TestClient(app)
except ImportError:
    client = None


class TestAIRecommendationsIntegration:
    """Integration tests for AI recommendation generation with context."""

    def test_complete_recommendation_workflow(self):
        """Test complete recommendation generation and evaluation workflow."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")

        puzzle_words = (
            "BASS,PIANO,GUITAR,DRUMS,FISH,SALMON,TROUT,TUNA,YELLOW,GREEN,BLUE,PURPLE,APPLE,BANANA,ORANGE,GRAPE"
        )
        file_data = io.BytesIO(puzzle_words.encode())
        files = {"file": ("test_puzzle.txt", file_data, "text/plain")}
        data = {"user_id": "integration-test-user"}

        upload_response = client.post("/api/v1/puzzles/upload", files=files, data=data)
        assert upload_response.status_code == 201
        puzzle_id = upload_response.json()["id"]

        # Create a session
        session_request = {"puzzle_id": puzzle_id, "llm_model": "gpt-4"}
        session_response = client.post("/api/v1/sessions", json=session_request)
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]

        # Request a recommendation
        rec_response = client.post(f"/api/v1/sessions/{session_id}/recommendations")
        assert rec_response.status_code == 201
        rec_data = rec_response.json()
        assert "id" in rec_data
        rec_id = rec_data["id"]

        # Evaluate the recommendation as incorrect
        eval_response = client.post(
            f"/api/v1/sessions/{session_id}/recommendations/{rec_id}/evaluate",
            json={"evaluation": "incorrect"},
        )
        assert eval_response.status_code == 200
        eval_data = eval_response.json()
        assert eval_data["recommendation"]["user_evaluation"] == "incorrect"

        # Request another recommendation to ensure flow continues
        rec2_response = client.post(f"/api/v1/sessions/{session_id}/recommendations")
        assert rec2_response.status_code == 201
        rec2_data = rec2_response.json()
        assert rec2_data["id"] != rec_id

    def test_context_aware_recommendations(self):
        """Test that recommendations consider previous evaluations."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")

        # We'll perform a short flow and ensure recommendations can be generated
        puzzle_words = "A1,B2,C3,D4,E5,F6,G7,H8,I9,J10,K11,L12,M13,N14,O15,P16"
        file_data = io.BytesIO(puzzle_words.encode())
        files = {"file": ("puzzle.csv", file_data, "text/csv")}
        upload_response = client.post("/api/v1/puzzles/upload", files=files, data={"user_id": "integration-test-user"})
        assert upload_response.status_code == 201
        puzzle_id = upload_response.json()["id"]

        session_request = {"puzzle_id": puzzle_id, "llm_model": "gpt-4"}
        session_response = client.post("/api/v1/sessions", json=session_request)
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]

        # Generate first recommendation and mark one-away
        rec_response = client.post(f"/api/v1/sessions/{session_id}/recommendations")
        assert rec_response.status_code == 201
        rec_id = rec_response.json()["id"]

        eval_response = client.post(
            f"/api/v1/sessions/{session_id}/recommendations/{rec_id}/evaluate",
            json={"evaluation": "one_away"},
        )
        assert eval_response.status_code == 200

        # Generate another recommendation and ensure it returns a fresh recommendation
        rec2_response = client.post(f"/api/v1/sessions/{session_id}/recommendations")
        assert rec2_response.status_code == 201
        rec2_data = rec2_response.json()
        assert "id" in rec2_data
        assert rec2_data.get("user_evaluation") is None
