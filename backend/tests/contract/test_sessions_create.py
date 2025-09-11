"""
Contract tests for POST /api/v1/sessions endpoint.

This test validates the API contract for creating new game sessions.
These tests MUST FAIL until the actual endpoint is implemented.

Test Scenarios:
- Create session with valid puzzle_id and LLM model
- Handle invalid puzzle_id (non-existent)
- Validate LLM model enumeration constraints
- Test optional user_id parameter
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


class TestSessionsCreateContract:
    """Contract tests for POST /api/v1/sessions endpoint."""

    def test_create_session_valid_request(self):
        """Test creating session with valid puzzle_id and LLM model."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        # Valid session creation request
        session_request = {
            "puzzle_id": "12345678-1234-5678-9abc-123456789012",
            "llm_model": "gpt-4",
            "user_id": "test-user-123",
        }

        response = client.post("/api/v1/sessions", json=session_request, headers={"Content-Type": "application/json"})

        # Contract validation: Status code
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        # Contract validation: Response structure
        json_data = response.json()
        required_fields = [
            "id",
            "puzzle_id",
            "start_time",
            "last_activity",
            "status",
            "remaining_words",
            "incorrect_evaluation_count",
            "solved_groups_count",
            "can_request_recommendation",
            "llm_model_config",
        ]
        for field in required_fields:
            assert field in json_data, f"Missing required field: {field}"

        # Contract validation: Field types and constraints
        assert isinstance(json_data["id"], str), "id must be string (UUID)"
        assert isinstance(json_data["puzzle_id"], str), "puzzle_id must be string (UUID)"
        assert json_data["puzzle_id"] == session_request["puzzle_id"], "puzzle_id must match request"

        assert isinstance(json_data["start_time"], str), "start_time must be string (datetime)"
        assert isinstance(json_data["last_activity"], str), "last_activity must be string (datetime)"

        assert isinstance(json_data["status"], str), "status must be string"
        assert json_data["status"] in [
            "active",
            "completed",
            "failed",
            "abandoned",
        ], f"status must be valid enum value, got: {json_data['status']}"

        assert isinstance(json_data["remaining_words"], list), "remaining_words must be list"
        assert len(json_data["remaining_words"]) == 16, "new session should have 16 remaining words"

        assert isinstance(json_data["incorrect_evaluation_count"], int), "incorrect_evaluation_count must be int"
        assert 0 <= json_data["incorrect_evaluation_count"] <= 4, "incorrect_evaluation_count must be 0-4"

        assert isinstance(json_data["solved_groups_count"], int), "solved_groups_count must be int"
        assert 0 <= json_data["solved_groups_count"] <= 4, "solved_groups_count must be 0-4"

        assert isinstance(json_data["can_request_recommendation"], bool), "can_request_recommendation must be bool"

        assert isinstance(json_data["llm_model_config"], str), "llm_model_config must be string"
        assert json_data["llm_model_config"] == session_request["llm_model"], "llm_model_config must match request"

    def test_create_session_without_user_id(self):
        """Test creating session without optional user_id (anonymous session)."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        session_request = {"puzzle_id": "87654321-4321-8765-4321-876543210987", "llm_model": "claude-3-sonnet"}

        response = client.post("/api/v1/sessions", json=session_request)

        assert response.status_code == 201
        json_data = response.json()

        # Should have all required fields
        assert "id" in json_data
        assert "puzzle_id" in json_data
        assert json_data["puzzle_id"] == session_request["puzzle_id"]
        assert json_data["llm_model_config"] == session_request["llm_model"]

    def test_create_session_all_llm_models(self):
        """Test session creation with all valid LLM models."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        valid_models = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "claude-3-haiku"]
        test_puzzle_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

        for model in valid_models:
            session_request = {"puzzle_id": test_puzzle_id, "llm_model": model}

            response = client.post("/api/v1/sessions", json=session_request)

            assert response.status_code == 201, f"Failed for model: {model}"
            json_data = response.json()
            assert json_data["llm_model_config"] == model, f"Model config mismatch for: {model}"

    def test_create_session_invalid_llm_model(self):
        """Test error response for invalid LLM model."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        session_request = {"puzzle_id": "12345678-1234-5678-9abc-123456789012", "llm_model": "invalid-model"}

        response = client.post("/api/v1/sessions", json=session_request)

        # Contract validation: Error response
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        json_data = response.json()
        assert "error" in json_data, "Error response must have 'error' field"
        assert "message" in json_data, "Error response must have 'message' field"
        assert isinstance(json_data["error"], str), "error field must be string"
        assert isinstance(json_data["message"], str), "message field must be string"

    def test_create_session_invalid_puzzle_id_format(self):
        """Test error response for invalid puzzle_id UUID format."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        session_request = {"puzzle_id": "not-a-valid-uuid", "llm_model": "gpt-4"}

        response = client.post("/api/v1/sessions", json=session_request)

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        json_data = response.json()
        assert "error" in json_data
        assert "message" in json_data

    def test_create_session_nonexistent_puzzle_id(self):
        """Test error response for non-existent puzzle_id."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        session_request = {"puzzle_id": "99999999-9999-9999-9999-999999999999", "llm_model": "gpt-4"}

        response = client.post("/api/v1/sessions", json=session_request)

        # Should return 400 for invalid puzzle reference
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        json_data = response.json()
        assert "error" in json_data
        assert "message" in json_data

    def test_create_session_missing_required_fields(self):
        """Test error response when required fields are missing."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        # Missing puzzle_id
        incomplete_request1 = {"llm_model": "gpt-4"}
        response1 = client.post("/api/v1/sessions", json=incomplete_request1)
        assert response1.status_code == 400

        # Missing llm_model
        incomplete_request2 = {"puzzle_id": "12345678-1234-5678-9abc-123456789012"}
        response2 = client.post("/api/v1/sessions", json=incomplete_request2)
        assert response2.status_code == 400

        # Empty request
        response3 = client.post("/api/v1/sessions", json={})
        assert response3.status_code == 400

    def test_create_session_initial_state_values(self):
        """Test that new session has correct initial state values."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        session_request = {"puzzle_id": "11111111-2222-3333-4444-555555555555", "llm_model": "gpt-3.5-turbo"}

        response = client.post("/api/v1/sessions", json=session_request)

        assert response.status_code == 201
        json_data = response.json()

        # Validate initial state
        assert json_data["status"] == "active", "New session should be active"
        assert json_data["incorrect_evaluation_count"] == 0, "New session should have 0 incorrect evaluations"
        assert json_data["solved_groups_count"] == 0, "New session should have 0 solved groups"
        assert json_data["can_request_recommendation"] is True, "New session should allow recommendations"

        # Optional fields validation
        if "pending_recommendation_id" in json_data:
            assert json_data["pending_recommendation_id"] is None, "New session should have no pending recommendation"

        if "solved_groups" in json_data:
            assert json_data["solved_groups"] == [], "New session should have empty solved_groups list"

    def test_create_session_datetime_format(self):
        """Test that datetime fields have proper format."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        session_request = {"puzzle_id": "22222222-3333-4444-5555-666666666666", "llm_model": "claude-3-haiku"}

        response = client.post("/api/v1/sessions", json=session_request)

        assert response.status_code == 201
        json_data = response.json()

        # Basic datetime format validation
        start_time = json_data["start_time"]
        last_activity = json_data["last_activity"]

        assert isinstance(start_time, str)
        assert isinstance(last_activity, str)
        # Should contain date/time separator
        assert "T" in start_time or " " in start_time
        assert "T" in last_activity or " " in last_activity
        # Minimum length for datetime
        assert len(start_time) >= 19
        assert len(last_activity) >= 19

    def test_create_session_malformed_json(self):
        """Test error response for malformed JSON."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        # Send malformed JSON
        response = client.post(
            "/api/v1/sessions",
            data='{"puzzle_id": "invalid-json"',  # Missing closing brace
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        json_data = response.json()
        assert "error" in json_data
        assert "message" in json_data

    def test_create_session_remaining_words_validation(self):
        """Test that remaining_words contains exactly the puzzle's words."""
        if client is None:
            pytest.fail("FastAPI app not implemented - contract test intentionally failing")

        session_request = {"puzzle_id": "33333333-4444-5555-6666-777777777777", "llm_model": "gpt-4"}

        response = client.post("/api/v1/sessions", json=session_request)

        assert response.status_code == 201
        json_data = response.json()

        remaining_words = json_data["remaining_words"]

        # Should have exactly 16 words for new session
        assert len(remaining_words) == 16, f"Expected 16 remaining words, got {len(remaining_words)}"

        # All remaining words should be strings
        for word in remaining_words:
            assert isinstance(word, str), f"Word must be string: {word}"
            assert len(word) > 0, f"Word cannot be empty: {word}"
            assert len(word) <= 20, f"Word too long: {word}"

        # All words should be unique
        assert len(set(remaining_words)) == 16, "All remaining words must be unique"
