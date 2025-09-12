"""WebSocket connection capacity testing.

Tests to ensure WebSocket infrastructure can handle high concurrent user loads:
- 100+ concurrent WebSocket connections
- Message broadcasting performance
- Connection management under load
- Memory usage with many connections
"""

import asyncio
import json
import pytest
import time
from typing import List
from unittest.mock import MagicMock

from src.websockets.recommendation_handler import ConnectionManager, RecommendationWebSocketHandler
from src.services.session_service import SessionService
from src.services.llm_service import LLMService
from src.services.context_service import ContextService


class MockWebSocket:
    """Mock WebSocket for testing."""

    def __init__(self, connection_id: str):
        self.connection_id = connection_id
        self.messages: List[str] = []
        self.closed = False
        self.accept_called = False

    async def accept(self):
        """Mock accept method."""
        self.accept_called = True

    async def send_text(self, message: str):
        """Mock send_text method."""
        if self.closed:
            raise Exception("Connection closed")
        self.messages.append(message)

    async def close(self):
        """Mock close method."""
        self.closed = True


class TestWebSocketCapacity:
    """Test WebSocket connection capacity and performance."""

    @pytest.fixture
    def connection_manager(self) -> ConnectionManager:
        """Create fresh connection manager for testing."""
        return ConnectionManager()

    @pytest.fixture
    def mock_services(self):
        """Create mock services for WebSocket handler."""
        session_service = MagicMock(spec=SessionService)
        llm_service = MagicMock(spec=LLMService)
        context_service = MagicMock(spec=ContextService)
        return session_service, llm_service, context_service

    @pytest.fixture
    def websocket_handler(self, mock_services):
        """Create WebSocket handler with mock services."""
        session_service, llm_service, context_service = mock_services
        return RecommendationWebSocketHandler(session_service, llm_service, context_service)

    @pytest.mark.asyncio
    async def test_100_concurrent_connections(self, connection_manager: ConnectionManager):
        """Test handling 100 concurrent WebSocket connections."""
        num_connections = 100
        session_id = "capacity-test-session"
        mock_websockets = []
        connection_ids = []

        start_time = time.time()

        # Create and connect 100 mock WebSockets
        for i in range(num_connections):
            connection_id = f"conn-{i}"
            mock_ws = MockWebSocket(connection_id)

            await connection_manager.connect(mock_ws, session_id, connection_id)

            mock_websockets.append(mock_ws)
            connection_ids.append(connection_id)

        connection_time = time.time() - start_time

        # Verify all connections are tracked
        assert len(connection_manager.active_connections) == num_connections
        assert session_id in connection_manager.session_connections
        assert len(connection_manager.session_connections[session_id]) == num_connections

        # Connection setup should be fast (under 1 second for 100 connections)
        assert connection_time < 1.0, f"Connection setup took {connection_time:.2f}s, should be under 1s"

        # Test message broadcasting to all connections
        test_message = json.dumps({"type": "test", "data": "capacity_test"})

        broadcast_start = time.time()
        await connection_manager.broadcast_to_session(test_message, session_id)
        broadcast_time = time.time() - broadcast_start

        # Broadcasting should be fast (under 0.5 seconds for 100 connections)
        assert broadcast_time < 0.5, f"Broadcasting took {broadcast_time:.2f}s, should be under 0.5s"

        # Verify all connections received the message
        for ws in mock_websockets:
            assert len(ws.messages) == 1
            assert ws.messages[0] == test_message

        # Clean up connections
        for i, connection_id in enumerate(connection_ids):
            connection_manager.disconnect(connection_id, session_id)

        # Verify cleanup
        assert len(connection_manager.active_connections) == 0
        assert session_id not in connection_manager.session_connections

    @pytest.mark.asyncio
    async def test_200_concurrent_connections(self, connection_manager: ConnectionManager):
        """Test handling 200 concurrent WebSocket connections (stress test)."""
        num_connections = 200
        session_id = "stress-test-session"

        start_time = time.time()

        # Create connections
        for i in range(num_connections):
            connection_id = f"stress-conn-{i}"
            mock_ws = MockWebSocket(connection_id)
            await connection_manager.connect(mock_ws, session_id, connection_id)

        connection_time = time.time() - start_time

        # Verify all connections are tracked
        assert len(connection_manager.active_connections) == num_connections

        # Should handle even 200 connections reasonably fast (under 2 seconds)
        assert connection_time < 2.0, f"200 connections took {connection_time:.2f}s, should be under 2s"

        # Test broadcasting performance with many connections
        test_message = json.dumps({"type": "stress_test", "timestamp": time.time()})

        broadcast_start = time.time()
        await connection_manager.broadcast_to_session(test_message, session_id)
        broadcast_time = time.time() - broadcast_start

        # Broadcasting to 200 connections should still be reasonable (under 1 second)
        assert broadcast_time < 1.0, f"Broadcasting to 200 connections took {broadcast_time:.2f}s"

    @pytest.mark.asyncio
    async def test_multiple_sessions_capacity(self, connection_manager: ConnectionManager):
        """Test capacity with multiple sessions and connections."""
        num_sessions = 10
        connections_per_session = 10
        total_connections = num_sessions * connections_per_session

        start_time = time.time()

        # Create connections across multiple sessions
        for session_idx in range(num_sessions):
            session_id = f"multi-session-{session_idx}"

            for conn_idx in range(connections_per_session):
                connection_id = f"multi-conn-{session_idx}-{conn_idx}"
                mock_ws = MockWebSocket(connection_id)
                await connection_manager.connect(mock_ws, session_id, connection_id)

        connection_time = time.time() - start_time

        # Verify tracking
        assert len(connection_manager.active_connections) == total_connections
        assert len(connection_manager.session_connections) == num_sessions

        # Connection time should be reasonable
        assert connection_time < 1.0, f"Multi-session setup took {connection_time:.2f}s"

        # Test broadcasting to individual sessions
        for session_idx in range(num_sessions):
            session_id = f"multi-session-{session_idx}"
            test_message = json.dumps({"session": session_idx, "type": "session_test"})

            await connection_manager.broadcast_to_session(test_message, session_id)

        # Verify session isolation (each session only gets its own messages)
        for session_idx in range(num_sessions):
            session_id = f"multi-session-{session_idx}"
            session_connections = connection_manager.session_connections[session_id]

            assert len(session_connections) == connections_per_session

            # Check that connections in this session received the right message
            for conn_id in session_connections:
                mock_ws = connection_manager.active_connections[conn_id]
                assert len(mock_ws.messages) == 1
                message_data = json.loads(mock_ws.messages[0])
                assert message_data["session"] == session_idx

    @pytest.mark.asyncio
    async def test_concurrent_message_sending(self, connection_manager: ConnectionManager):
        """Test concurrent message sending to many connections."""
        num_connections = 50
        num_messages = 10
        session_id = "concurrent-msg-test"

        # Set up connections
        for i in range(num_connections):
            connection_id = f"concurrent-conn-{i}"
            mock_ws = MockWebSocket(connection_id)
            await connection_manager.connect(mock_ws, session_id, connection_id)

        start_time = time.time()

        # Send multiple messages concurrently
        async def send_message_batch(batch_id: int):
            """Send a batch of messages."""
            message = json.dumps({"batch": batch_id, "timestamp": time.time()})
            await connection_manager.broadcast_to_session(message, session_id)

        # Send messages concurrently
        tasks = [send_message_batch(i) for i in range(num_messages)]
        await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        # Should handle concurrent messaging efficiently
        assert total_time < 2.0, f"Concurrent messaging took {total_time:.2f}s, should be under 2s"

        # Verify all connections received all messages
        for connection_id in connection_manager.active_connections:
            mock_ws = connection_manager.active_connections[connection_id]
            assert len(mock_ws.messages) == num_messages

    @pytest.mark.asyncio
    async def test_connection_failure_handling(self, connection_manager: ConnectionManager):
        """Test handling of connection failures under load."""
        num_connections = 100
        session_id = "failure-test-session"

        # Create connections, some of which will "fail"
        failing_connections = set()
        for i in range(num_connections):
            connection_id = f"failure-conn-{i}"
            mock_ws = MockWebSocket(connection_id)

            # Mark some connections as failing
            if i % 10 == 0:  # Every 10th connection will fail
                mock_ws.closed = True
                failing_connections.add(connection_id)

            await connection_manager.connect(mock_ws, session_id, connection_id)

        # Attempt to broadcast - should handle failures gracefully
        test_message = json.dumps({"type": "failure_test"})

        start_time = time.time()
        await connection_manager.broadcast_to_session(test_message, session_id)
        broadcast_time = time.time() - start_time

        # Should complete reasonably fast even with failures
        assert broadcast_time < 1.0, f"Broadcast with failures took {broadcast_time:.2f}s"

        # Verify working connections received messages
        working_connections = 0
        for connection_id, mock_ws in connection_manager.active_connections.items():
            if not mock_ws.closed:
                assert len(mock_ws.messages) >= 1
                working_connections += 1

        # Should have fewer active connections due to failures being removed
        expected_working = num_connections - len(failing_connections)
        assert working_connections <= expected_working

    @pytest.mark.asyncio
    async def test_memory_efficiency_many_connections(self, connection_manager: ConnectionManager):
        """Test memory efficiency with many connections."""
        num_connections = 150
        session_id = "memory-test-session"

        # Create many connections
        for i in range(num_connections):
            connection_id = f"memory-conn-{i}"
            mock_ws = MockWebSocket(connection_id)
            await connection_manager.connect(mock_ws, session_id, connection_id)

        # Send multiple rounds of messages
        for round_num in range(5):
            message = json.dumps({"round": round_num, "data": "x" * 100, "timestamp": time.time()})  # Some data payload
            await connection_manager.broadcast_to_session(message, session_id)

        # Verify connections are still tracked correctly
        assert len(connection_manager.active_connections) == num_connections
        assert len(connection_manager.session_connections[session_id]) == num_connections

        # Clean up all connections
        connection_ids = list(connection_manager.active_connections.keys())
        for connection_id in connection_ids:
            connection_manager.disconnect(connection_id, session_id)

        # Verify complete cleanup
        assert len(connection_manager.active_connections) == 0
        assert session_id not in connection_manager.session_connections

    @pytest.mark.asyncio
    async def test_rapid_connect_disconnect(self, connection_manager: ConnectionManager):
        """Test rapid connection and disconnection cycles."""
        session_id = "rapid-cycle-test"
        num_cycles = 50

        start_time = time.time()

        for cycle in range(num_cycles):
            # Connect 10 connections
            connection_ids = []
            for i in range(10):
                connection_id = f"rapid-{cycle}-{i}"
                mock_ws = MockWebSocket(connection_id)
                await connection_manager.connect(mock_ws, session_id, connection_id)
                connection_ids.append(connection_id)

            # Send a message
            message = json.dumps({"cycle": cycle, "type": "rapid_test"})
            await connection_manager.broadcast_to_session(message, session_id)

            # Disconnect all connections
            for connection_id in connection_ids:
                connection_manager.disconnect(connection_id, session_id)

        total_time = time.time() - start_time

        # Should handle rapid cycles efficiently
        assert total_time < 5.0, f"Rapid connect/disconnect cycles took {total_time:.2f}s"

        # Should be clean at the end
        assert len(connection_manager.active_connections) == 0
        assert session_id not in connection_manager.session_connections


class TestWebSocketPerformanceMetrics:
    """Test specific performance metrics for WebSocket operations."""

    @pytest.fixture
    def connection_manager(self) -> ConnectionManager:
        """Create fresh connection manager for testing."""
        return ConnectionManager()

    @pytest.mark.asyncio
    async def test_connection_establishment_speed(self, connection_manager: ConnectionManager):
        """Test speed of individual connection establishment."""
        session_id = "speed-test-session"

        # Test individual connection speed
        connection_times = []
        for i in range(20):
            connection_id = f"speed-conn-{i}"
            mock_ws = MockWebSocket(connection_id)

            start_time = time.time()
            await connection_manager.connect(mock_ws, session_id, connection_id)
            connection_time = time.time() - start_time

            connection_times.append(connection_time)

        # Each connection should be very fast (under 10ms)
        avg_time = sum(connection_times) / len(connection_times)
        max_time = max(connection_times)

        assert avg_time < 0.01, f"Average connection time {avg_time:.3f}s too slow"
        assert max_time < 0.05, f"Max connection time {max_time:.3f}s too slow"

    @pytest.mark.asyncio
    async def test_message_broadcast_latency(self, connection_manager: ConnectionManager):
        """Test message broadcast latency with different connection counts."""
        session_id = "latency-test-session"

        # Test with different numbers of connections
        for num_connections in [10, 50, 100]:
            # Set up connections
            for i in range(num_connections):
                connection_id = f"latency-conn-{num_connections}-{i}"
                mock_ws = MockWebSocket(connection_id)
                await connection_manager.connect(mock_ws, session_id, connection_id)

            # Measure broadcast time
            message = json.dumps({"test": "latency", "connections": num_connections})

            start_time = time.time()
            await connection_manager.broadcast_to_session(message, session_id)
            broadcast_time = time.time() - start_time

            # Broadcast time should scale reasonably
            max_allowed_time = 0.01 * num_connections / 10  # Scale with connection count
            assert (
                broadcast_time < max_allowed_time
            ), f"Broadcast to {num_connections} connections took {broadcast_time:.3f}s"

            # Clean up for next test
            for i in range(num_connections):
                connection_id = f"latency-conn-{num_connections}-{i}"
                connection_manager.disconnect(connection_id, session_id)

    @pytest.mark.asyncio
    async def test_throughput_measurement(self, connection_manager: ConnectionManager):
        """Test message throughput with many connections."""
        num_connections = 100
        num_messages = 50
        session_id = "throughput-test-session"

        # Set up connections
        for i in range(num_connections):
            connection_id = f"throughput-conn-{i}"
            mock_ws = MockWebSocket(connection_id)
            await connection_manager.connect(mock_ws, session_id, connection_id)

        # Measure throughput
        start_time = time.time()

        for msg_idx in range(num_messages):
            message = json.dumps({"message_id": msg_idx, "data": f"throughput_test_{msg_idx}"})
            await connection_manager.broadcast_to_session(message, session_id)

        total_time = time.time() - start_time

        # Calculate throughput metrics
        total_message_deliveries = num_connections * num_messages
        throughput = total_message_deliveries / total_time

        # Should achieve reasonable throughput (at least 1000 messages/second)
        assert throughput > 1000, f"Throughput {throughput:.0f} msg/s too low"

        # Verify all messages were delivered
        for connection_id in connection_manager.active_connections:
            mock_ws = connection_manager.active_connections[connection_id]
            assert len(mock_ws.messages) == num_messages
