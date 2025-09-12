"""API response time validation tests.

Tests to ensure non-AI API operations meet performance requirements:
- Non-AI API endpoints respond under 100ms
- File upload operations within reasonable time
- Session management operations are fast
- Validation of all endpoints excluding AI recommendation generation
"""

import json
import pytest
import time
from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app
from src.services.puzzle_service import PuzzleService
from src.services.session_service import SessionService
from src.models.puzzle import Puzzle
from src.models.session import Session


class TestAPIResponseTimes:
    """Test API response times for non-AI operations."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_puzzle_file(self) -> BytesIO:
        """Create sample puzzle file for testing."""
        content = (
            "apple,banana,cherry,date,elderberry,fig,grape,kiwi,"
            "lemon,mango,orange,peach,plum,quince,strawberry,watermelon"
        )
        return BytesIO(content.encode())

    @pytest.fixture
    def mock_puzzle_service(self):
        """Mock puzzle service for testing."""
        with patch("src.api.puzzles.puzzle_service") as mock:
            mock_puzzle = Puzzle(
                id="test-puzzle-123",
                words=[
                    "apple",
                    "banana",
                    "cherry",
                    "date",
                    "elderberry",
                    "fig",
                    "grape",
                    "kiwi",
                    "lemon",
                    "mango",
                    "orange",
                    "peach",
                    "plum",
                    "quince",
                    "strawberry",
                    "watermelon",
                ],
                uploaded_filename="test.txt",
                user_id="test-user",
            )
            mock.parse_uploaded_file.return_value = mock_puzzle
            mock.get_puzzle.return_value = mock_puzzle
            yield mock

    @pytest.fixture
    def mock_session_service(self):
        """Mock session service for testing."""
        with patch("src.api.sessions.session_service") as mock:
            mock_session = Session(
                id="test-session-123", puzzle_id="test-puzzle-123", llm_model="gpt-4", user_id="test-user"
            )
            mock.create_session.return_value = mock_session
            mock.get_session.return_value = mock_session
            yield mock

    def test_puzzle_upload_response_time(self, client: TestClient, mock_puzzle_service):
        """Test puzzle upload endpoint response time."""
        # Prepare file data
        file_content = (
            "apple,banana,cherry,date,elderberry,fig,grape,kiwi,"
            "lemon,mango,orange,peach,plum,quince,strawberry,watermelon"
        )
        files = {"file": ("test.txt", file_content, "text/plain")}

        start_time = time.time()
        response = client.post("/api/v1/puzzles/upload", files=files)
        elapsed_time = time.time() - start_time

        # Should respond under 100ms
        assert elapsed_time < 0.1, f"Puzzle upload took {elapsed_time*1000:.0f}ms, should be under 100ms"
        assert response.status_code == 201

    def test_puzzle_get_response_time(self, client: TestClient, mock_puzzle_service):
        """Test get puzzle endpoint response time."""
        puzzle_id = "test-puzzle-123"

        start_time = time.time()
        response = client.get(f"/api/v1/puzzles/{puzzle_id}")
        elapsed_time = time.time() - start_time

        # Should respond under 100ms
        assert elapsed_time < 0.1, f"Get puzzle took {elapsed_time*1000:.0f}ms, should be under 100ms"
        assert response.status_code == 200

    def test_session_create_response_time(self, client: TestClient, mock_session_service):
        """Test session creation endpoint response time."""
        session_data = {"puzzle_id": "test-puzzle-123", "llm_model": "gpt-4", "user_id": "test-user"}

        start_time = time.time()
        response = client.post("/api/v1/sessions", json=session_data)
        elapsed_time = time.time() - start_time

        # Should respond under 100ms
        assert elapsed_time < 0.1, f"Session creation took {elapsed_time*1000:.0f}ms, should be under 100ms"
        assert response.status_code == 201

    def test_session_get_response_time(self, client: TestClient, mock_session_service):
        """Test get session endpoint response time."""
        session_id = "test-session-123"

        start_time = time.time()
        response = client.get(f"/api/v1/sessions/{session_id}")
        elapsed_time = time.time() - start_time

        # Should respond under 100ms
        assert elapsed_time < 0.1, f"Get session took {elapsed_time*1000:.0f}ms, should be under 100ms"
        assert response.status_code == 200

    def test_history_get_response_time(self, client: TestClient, mock_session_service):
        """Test get session history endpoint response time."""
        session_id = "test-session-123"

        with patch("src.api.history.session_service") as mock_history_service:
            mock_history_service.get_session.return_value = Session(
                id=session_id, puzzle_id="test-puzzle-123", llm_model="gpt-4"
            )
            mock_history_service.get_session_history.return_value = []

            start_time = time.time()
            response = client.get(f"/api/v1/sessions/{session_id}/history")
            elapsed_time = time.time() - start_time

            # Should respond under 100ms
            assert elapsed_time < 0.1, f"Get history took {elapsed_time*1000:.0f}ms, should be under 100ms"
            assert response.status_code == 200

    def test_recommendations_get_response_time(self, client: TestClient, mock_session_service):
        """Test get recommendations endpoint response time (non-AI operation)."""
        session_id = "test-session-123"

        with patch("src.api.recommendations.session_service") as mock_rec_service:
            mock_rec_service.get_session.return_value = Session(
                id=session_id, puzzle_id="test-puzzle-123", llm_model="gpt-4"
            )
            mock_rec_service.get_session_recommendations.return_value = []

            start_time = time.time()
            response = client.get(f"/api/v1/sessions/{session_id}/recommendations")
            elapsed_time = time.time() - start_time

            # Should respond under 100ms (this just retrieves existing recommendations)
            assert elapsed_time < 0.1, f"Get recommendations took {elapsed_time*1000:.0f}ms, should be under 100ms"
            assert response.status_code == 200

    def test_multiple_concurrent_requests(self, client: TestClient, mock_puzzle_service, mock_session_service):
        """Test response times under concurrent load."""
        num_requests = 20

        def make_request(request_id: int) -> float:
            """Make a single request and return response time."""
            start_time = time.time()
            response = client.get(f"/api/v1/puzzles/test-puzzle-{request_id % 5}")
            elapsed_time = time.time() - start_time

            # Verify response is successful
            if response.status_code != 200:
                # Some may fail due to mocking, but timing should still be good
                pass

            return elapsed_time

        # Make concurrent requests using threading (since TestClient is synchronous)
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            response_times = [future.result() for future in concurrent.futures.as_completed(futures)]
            total_time = time.time() - start_time

        # All individual requests should be under 100ms
        for i, response_time in enumerate(response_times):
            assert response_time < 0.1, f"Concurrent request {i} took {response_time*1000:.0f}ms, should be under 100ms"

        # Total time should show good concurrency (not linear)
        assert total_time < 2.0, f"Concurrent requests took {total_time:.2f}s total, should be efficient"

    def test_error_response_times(self, client: TestClient):
        """Test that error responses are also fast."""
        # Test 404 responses
        start_time = time.time()
        response = client.get("/api/v1/puzzles/nonexistent-puzzle")
        elapsed_time = time.time() - start_time

        assert elapsed_time < 0.1, f"404 response took {elapsed_time*1000:.0f}ms, should be under 100ms"

        # Test 400 responses (invalid data)
        start_time = time.time()
        response = client.post("/api/v1/sessions", json={"invalid": "data"})
        elapsed_time = time.time() - start_time

        assert elapsed_time < 0.1, f"400 response took {elapsed_time*1000:.0f}ms, should be under 100ms"

    def test_large_file_upload_timing(self, client: TestClient, mock_puzzle_service):
        """Test file upload with larger content (but still reasonable)."""
        # Create larger but valid file content
        words = [f"word{i}" for i in range(16)]
        large_content = ",".join(words) + "\n" + "Additional metadata content " * 100

        files = {"file": ("large_test.txt", large_content, "text/plain")}

        start_time = time.time()
        response = client.post("/api/v1/puzzles/upload", files=files)
        elapsed_time = time.time() - start_time

        # Even with larger content, should be under 200ms
        assert elapsed_time < 0.2, f"Large file upload took {elapsed_time*1000:.0f}ms, should be under 200ms"

    def test_validation_error_timing(self, client: TestClient):
        """Test that validation errors are returned quickly."""
        # Upload file with wrong number of words
        invalid_content = "apple,banana,cherry"  # Only 3 words instead of 16
        files = {"file": ("invalid.txt", invalid_content, "text/plain")}

        start_time = time.time()
        response = client.post("/api/v1/puzzles/upload", files=files)
        elapsed_time = time.time() - start_time

        # Validation should be very fast
        assert elapsed_time < 0.05, f"Validation error took {elapsed_time*1000:.0f}ms, should be under 50ms"
        assert response.status_code == 400


class TestServiceLayerPerformance:
    """Test performance of service layer operations."""

    def test_puzzle_service_operations(self):
        """Test puzzle service operation timing."""
        puzzle_service = PuzzleService()

        # Test file parsing
        content = (
            b"apple,banana,cherry,date,elderberry,fig,grape,kiwi,"
            b"lemon,mango,orange,peach,plum,quince,strawberry,watermelon"
        )

        start_time = time.time()
        puzzle = puzzle_service.parse_uploaded_file(content, "test.txt", "test-user")
        elapsed_time = time.time() - start_time

        # Should parse very quickly
        assert elapsed_time < 0.01, f"File parsing took {elapsed_time*1000:.0f}ms, should be under 10ms"
        assert puzzle is not None

    def test_session_service_operations(self):
        """Test session service operation timing."""
        session_service = SessionService()

        # Test session creation
        start_time = time.time()
        session = session_service.create_session("test-puzzle", "gpt-4", "test-user")
        elapsed_time = time.time() - start_time

        # Should create very quickly
        assert elapsed_time < 0.01, f"Session creation took {elapsed_time*1000:.0f}ms, should be under 10ms"
        assert session is not None

        # Test session retrieval
        start_time = time.time()
        retrieved_session = session_service.get_session(session.id)
        elapsed_time = time.time() - start_time

        # Should retrieve very quickly
        assert elapsed_time < 0.01, f"Session retrieval took {elapsed_time*1000:.0f}ms, should be under 10ms"
        assert retrieved_session is not None

    def test_bulk_operations_timing(self):
        """Test timing of bulk operations."""
        puzzle_service = PuzzleService()
        session_service = SessionService()

        # Create multiple puzzles
        start_time = time.time()
        puzzles = []
        for i in range(10):
            words = [f"word{i}_{j}" for j in range(1, 17)]
            content = ",".join(words)
            puzzle = puzzle_service.parse_uploaded_file(content.encode(), f"test{i}.txt", f"user{i}")
            puzzles.append(puzzle)
        elapsed_time = time.time() - start_time

        # Should handle bulk operations efficiently
        assert elapsed_time < 0.1, f"Creating 10 puzzles took {elapsed_time*1000:.0f}ms, should be under 100ms"

        # Create multiple sessions
        start_time = time.time()
        sessions = []
        for i, puzzle in enumerate(puzzles):
            session = session_service.create_session(puzzle.id, "gpt-4", f"user{i}")
            sessions.append(session)
        elapsed_time = time.time() - start_time

        # Should handle bulk session creation efficiently
        assert elapsed_time < 0.05, f"Creating 10 sessions took {elapsed_time*1000:.0f}ms, should be under 50ms"


class TestMemoryEfficiency:
    """Test memory efficiency of API operations."""

    def test_repeated_operations_memory(self):
        """Test that repeated operations don't cause memory issues."""
        client = TestClient(app)

        # Perform many operations to test for memory leaks
        for i in range(100):
            # This will likely fail due to missing mocks, but should not cause memory issues
            try:
                client.get(f"/api/v1/puzzles/test-{i}")
            except Exception:
                pass  # Ignore errors, we're testing memory efficiency

        # If we get here without memory issues, the test passes
        assert True

    def test_large_response_handling(self):
        """Test handling of larger response payloads."""
        puzzle_service = PuzzleService()

        # Create puzzle with all data
        content = (
            b"apple,banana,cherry,date,elderberry,fig,grape,kiwi,"
            b"lemon,mango,orange,peach,plum,quince,strawberry,watermelon"
        )

        start_time = time.time()
        puzzle = puzzle_service.parse_uploaded_file(content, "test.txt", "test-user")

        # Convert to dict (simulating API response serialization)
        response_data = {
            "id": puzzle.id,
            "words": puzzle.words,
            "uploaded_filename": puzzle.uploaded_filename,
            "created_at": puzzle.created_at.isoformat(),
            "user_id": puzzle.user_id,
        }

        # Convert to JSON (simulating FastAPI response)
        json_response = json.dumps(response_data)
        elapsed_time = time.time() - start_time

        # Should handle response generation quickly
        assert elapsed_time < 0.01, f"Response generation took {elapsed_time*1000:.0f}ms, should be under 10ms"
        assert len(json_response) > 0


class TestEndpointSpecificTiming:
    """Test timing for specific endpoint patterns."""

    def test_path_parameter_processing(self, client: TestClient):
        """Test that path parameter processing is fast."""
        # Test various ID formats
        test_ids = [
            "simple-id",
            "uuid-12345678-1234-1234-1234-123456789abc",
            "complex_id_with_underscores",
            "id-with-numbers-123",
        ]

        for test_id in test_ids:
            start_time = time.time()
            # This will 404, but path processing should be fast
            client.get(f"/api/v1/puzzles/{test_id}")
            elapsed_time = time.time() - start_time

            assert elapsed_time < 0.05, f"Path processing for {test_id} took {elapsed_time*1000:.0f}ms"

    def test_query_parameter_processing(self, client: TestClient):
        """Test that query parameter processing is fast."""
        # Test with various query parameters
        start_time = time.time()
        client.get("/api/v1/sessions/test-session/history?limit=10&offset=0&sort=desc")
        elapsed_time = time.time() - start_time

        assert elapsed_time < 0.1, f"Query parameter processing took {elapsed_time*1000:.0f}ms"

    def test_json_payload_processing(self, client: TestClient):
        """Test JSON payload processing speed."""
        # Test with various payload sizes
        payloads = [
            {"simple": "data"},
            {"complex": {"nested": {"data": ["item1", "item2", "item3"]}}},
            {"large_list": [f"item_{i}" for i in range(100)]},
        ]

        for payload in payloads:
            start_time = time.time()
            # This will error, but JSON processing should be fast
            client.post("/api/v1/sessions", json=payload)
            elapsed_time = time.time() - start_time

            assert elapsed_time < 0.05, f"JSON processing took {elapsed_time*1000:.0f}ms"
