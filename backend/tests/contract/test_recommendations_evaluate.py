"""
Contract tests for POST /api/v1/sessions/{session_id}/recommendations/{recommendation_id}/evaluate endpoint.

This test validates the API contract for evaluating AI recommendations.
These tests MUST FAIL until the actual endpoint is implemented.

Test Scenarios:
- Evaluate recommendation as correct/incorrect/one-away
- Handle non-existent recommendations
- Validate response structure and evaluation results
- Session state updates after evaluation
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


class TestRecommendationsEvaluateContract:
    """Contract tests for POST evaluate recommendation endpoint."""

    def test_evaluate_recommendation_correct(self):
        """Test evaluating recommendation as correct."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_session_id = "12345678-1234-5678-9abc-123456789012"
        test_recommendation_id = "87654321-4321-8765-4321-876543210987"

        evaluation_request = {"evaluation": "correct"}

        response = client.post(
            f"/api/v1/sessions/{test_session_id}/recommendations/{test_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        # Contract validation: Status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Contract validation: Response structure
        json_data = response.json()
        required_fields = ["recommendation", "session_status", "next_action"]
        for field in required_fields:
            assert field in json_data, f"Missing required field: {field}"

        # Contract validation: Recommendation object
        recommendation = json_data["recommendation"]
        assert isinstance(recommendation, dict), "recommendation must be dict"
        assert "id" in recommendation
        assert "user_evaluation" in recommendation
        assert "evaluation_timestamp" in recommendation
        assert recommendation["user_evaluation"] == "correct"
        assert recommendation["evaluation_timestamp"] is not None

        # Contract validation: Session status
        session_status = json_data["session_status"]
        assert session_status in [
            "active",
            "completed",
            "failed",
        ], f"session_status must be valid enum, got: {session_status}"

        # Contract validation: Next action
        next_action = json_data["next_action"]
        assert next_action in [
            "request_next_recommendation",
            "view_history",
            "game_complete",
        ], f"next_action must be valid enum, got: {next_action}"

        # Contract validation: Solved group (should be present for correct evaluation)
        if "solved_group" in json_data and json_data["solved_group"] is not None:
            solved_group = json_data["solved_group"]
            assert isinstance(solved_group, dict)
            assert "theme" in solved_group
            assert "difficulty" in solved_group
            assert "words" in solved_group
            assert isinstance(solved_group["words"], list)
            assert len(solved_group["words"]) == 4
            assert solved_group["difficulty"] in ["yellow", "green", "blue", "purple"]

    def test_evaluate_recommendation_incorrect(self):
        """Test evaluating recommendation as incorrect."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_session_id = "11111111-2222-3333-4444-555555555555"
        test_recommendation_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

        evaluation_request = {"evaluation": "incorrect"}

        response = client.post(
            f"/api/v1/sessions/{test_session_id}/recommendations/{test_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        assert response.status_code == 200
        json_data = response.json()

        # Validate evaluation was recorded
        recommendation = json_data["recommendation"]
        assert recommendation["user_evaluation"] == "incorrect"
        assert recommendation["evaluation_timestamp"] is not None

        # For incorrect evaluation, no solved_group should be present
        if "solved_group" in json_data:
            assert json_data["solved_group"] is None

    def test_evaluate_recommendation_one_away(self):
        """Test evaluating recommendation as one-away."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_session_id = "22222222-3333-4444-5555-666666666666"
        test_recommendation_id = "ffff1111-2222-3333-4444-555566667777"

        evaluation_request = {"evaluation": "one_away"}

        response = client.post(
            f"/api/v1/sessions/{test_session_id}/recommendations/{test_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        assert response.status_code == 200
        json_data = response.json()

        # Validate evaluation was recorded
        recommendation = json_data["recommendation"]
        assert recommendation["user_evaluation"] == "one_away"
        assert recommendation["evaluation_timestamp"] is not None

        # For one-away evaluation, no solved_group should be present
        if "solved_group" in json_data:
            assert json_data["solved_group"] is None

    def test_evaluate_recommendation_invalid_evaluation(self):
        """Test error response for invalid evaluation value."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_session_id = "33333333-4444-5555-6666-777777777777"
        test_recommendation_id = "12ab34cd-56ef-78gh-90ij-klmnopqrstuv"

        evaluation_request = {"evaluation": "invalid_value"}

        response = client.post(
            f"/api/v1/sessions/{test_session_id}/recommendations/{test_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        # Contract validation: Error response
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        json_data = response.json()
        assert "error" in json_data, "Error response must have 'error' field"
        assert "message" in json_data, "Error response must have 'message' field"
        assert isinstance(json_data["error"], str), "error field must be string"
        assert isinstance(json_data["message"], str), "message field must be string"

    def test_evaluate_recommendation_missing_evaluation(self):
        """Test error response when evaluation field is missing."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_session_id = "44444444-5555-6666-7777-888888888888"
        test_recommendation_id = "55555555-6666-7777-8888-999999999999"

        # Missing required evaluation field
        evaluation_request = {}

        response = client.post(
            f"/api/v1/sessions/{test_session_id}/recommendations/{test_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        assert response.status_code == 400
        json_data = response.json()
        assert "error" in json_data
        assert "message" in json_data

    def test_evaluate_nonexistent_recommendation(self):
        """Test error response for non-existent recommendation ID."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_session_id = "66666666-7777-8888-9999-aaaaaaaaaaaa"
        nonexistent_recommendation_id = "99999999-9999-9999-9999-999999999999"

        evaluation_request = {"evaluation": "correct"}

        response = client.post(
            f"/api/v1/sessions/{test_session_id}/recommendations/{nonexistent_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        # Contract validation: Not found response
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

        json_data = response.json()
        assert "error" in json_data
        assert "message" in json_data

    def test_evaluate_nonexistent_session(self):
        """Test error response for non-existent session ID."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        nonexistent_session_id = "99999999-9999-9999-9999-999999999999"
        test_recommendation_id = "77777777-8888-9999-aaaa-bbbbbbbbbbbb"

        evaluation_request = {"evaluation": "incorrect"}

        response = client.post(
            f"/api/v1/sessions/{nonexistent_session_id}/recommendations/{test_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        # Should return 404 for non-existent session
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

        json_data = response.json()
        assert "error" in json_data
        assert "message" in json_data

    def test_evaluate_invalid_session_uuid(self):
        """Test error response for invalid session UUID format."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        invalid_session_id = "not-a-valid-uuid"
        test_recommendation_id = "88888888-9999-aaaa-bbbb-cccccccccccc"

        evaluation_request = {"evaluation": "one_away"}

        response = client.post(
            f"/api/v1/sessions/{invalid_session_id}/recommendations/{test_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        json_data = response.json()
        assert "error" in json_data
        assert "message" in json_data

    def test_evaluate_invalid_recommendation_uuid(self):
        """Test error response for invalid recommendation UUID format."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_session_id = "99999999-aaaa-bbbb-cccc-dddddddddddd"
        invalid_recommendation_id = "not-a-valid-uuid"

        evaluation_request = {"evaluation": "correct"}

        response = client.post(
            f"/api/v1/sessions/{test_session_id}/recommendations/{invalid_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        json_data = response.json()
        assert "error" in json_data
        assert "message" in json_data

    def test_evaluate_recommendation_timestamp_format(self):
        """Test that evaluation_timestamp has proper datetime format."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_session_id = "aaaaaaaa-bbbb-cccc-dddd-111111111111"
        test_recommendation_id = "bbbbbbbb-cccc-dddd-eeee-222222222222"

        evaluation_request = {"evaluation": "incorrect"}

        response = client.post(
            f"/api/v1/sessions/{test_session_id}/recommendations/{test_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        if response.status_code == 200:
            json_data = response.json()
            recommendation = json_data["recommendation"]
            evaluation_timestamp = recommendation["evaluation_timestamp"]

            # Basic datetime format validation
            assert isinstance(evaluation_timestamp, str)
            assert "T" in evaluation_timestamp or " " in evaluation_timestamp
            assert len(evaluation_timestamp) >= 19

    def test_evaluate_session_status_transitions(self):
        """Test that session_status reflects proper state transitions."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_session_id = "cccccccc-dddd-eeee-ffff-333333333333"
        test_recommendation_id = "dddddddd-eeee-ffff-gggg-444444444444"

        evaluation_request = {"evaluation": "correct"}

        response = client.post(
            f"/api/v1/sessions/{test_session_id}/recommendations/{test_recommendation_id}/evaluate",
            json=evaluation_request,
        )

        if response.status_code == 200:
            json_data = response.json()
            session_status = json_data["session_status"]
            next_action = json_data["next_action"]

            # Validate status-action consistency
            if session_status == "completed":
                assert next_action in ["view_history", "game_complete"]
            elif session_status == "failed":
                assert next_action in ["view_history"]
            elif session_status == "active":
                assert next_action in ["request_next_recommendation", "view_history"]

    def test_evaluate_malformed_json(self):
        """Test error response for malformed JSON."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        test_session_id = "eeeeeeee-ffff-gggg-hhhh-555555555555"
        test_recommendation_id = "ffffffff-gggg-hhhh-iiii-666666666666"

        # Send malformed JSON
        response = client.post(
            f"/api/v1/sessions/{test_session_id}/recommendations/{test_recommendation_id}/evaluate",
            data='{"evaluation": "correct"',  # Missing closing brace
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        json_data = response.json()
        assert "error" in json_data
        assert "message" in json_data
