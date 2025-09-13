"""
Integration test for evaluation workflow (correct/incorrect/one-away).

This test validates the end-to-end evaluation functionality.
These tests MUST FAIL until the actual implementation is complete.
"""

import pytest
from fastapi.testclient import TestClient
import io

try:
    from src.main import app

    client = TestClient(app)
except ImportError:
    client = None


class TestEvaluationFlowIntegration:
    """Integration tests for evaluation workflow."""

    def test_complete_evaluation_workflow(self):
        """Test complete evaluation workflow with state transitions."""
        if client is None:
            pytest.fail("FastAPI app not implemented - integration test intentionally failing")
        # Upload a puzzle and create session
        puzzle_words = "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P"
        file_data = io.BytesIO(puzzle_words.encode())
        files = {"file": ("eval_test.txt", file_data, "text/plain")}

        upload_response = client.post("/api/v1/puzzles/upload", files=files)
        assert upload_response.status_code == 201
        puzzle_id = upload_response.json()["id"]

        session_response = client.post("/api/v1/sessions", json={"puzzle_id": puzzle_id, "llm_model": "gpt-4"})
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]

        # Request recommendation
        rec_response = client.post(f"/api/v1/sessions/{session_id}/recommendations")
        assert rec_response.status_code == 201
        rec_id = rec_response.json()["id"]

        # Evaluate as correct and ensure session updates
        eval_response = client.post(
            f"/api/v1/sessions/{session_id}/recommendations/{rec_id}/evaluate",
            json={"evaluation": "correct"},
        )
        assert eval_response.status_code == 200
        data = eval_response.json()
        assert data["recommendation"]["user_evaluation"] == "correct"
