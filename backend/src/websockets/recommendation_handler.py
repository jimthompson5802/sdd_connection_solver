"""
WebSocket connection handler for real-time AI recommendations.

This module provides WebSocket communication for delivering real-time AI
recommendations to connected clients during puzzle-solving sessions.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

from ..models.session import Session
from ..models.recommendation import Recommendation
from ..services.session_service import SessionService
from ..services.llm_service import LLMService
from ..services.context_service import ContextService


logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time recommendations."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, connection_id: str):
        """
        Accept a new WebSocket connection and associate it with a session.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier
            connection_id: Unique connection identifier

        Raises:
            HTTPException: If session is invalid
        """
        await websocket.accept()

        # Store connection
        self.active_connections[connection_id] = websocket

        # Associate with session
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection_id)

        logger.info(f"WebSocket connection {connection_id} established for session {session_id}")

    def disconnect(self, connection_id: str, session_id: str):
        """
        Remove WebSocket connection from active connections.

        Args:
            connection_id: Connection identifier to remove
            session_id: Session identifier
        """
        # Remove from active connections
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from session associations
        if session_id in self.session_connections:
            self.session_connections[session_id].discard(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]

        logger.info(f"WebSocket connection {connection_id} disconnected from session {session_id}")

    async def send_personal_message(self, message: str, connection_id: str):
        """
        Send message to a specific connection.

        Args:
            message: JSON message to send
            connection_id: Target connection identifier
        """
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to connection {connection_id}: {e}")
                # Remove broken connection
                await self._remove_broken_connection(connection_id)

    async def broadcast_to_session(self, message: str, session_id: str):
        """
        Send message to all connections in a session.

        Args:
            message: JSON message to send
            session_id: Target session identifier
        """
        if session_id not in self.session_connections:
            logger.warning(f"No connections found for session {session_id}")
            return

        connection_ids = list(self.session_connections[session_id])
        for connection_id in connection_ids:
            await self.send_personal_message(message, connection_id)

    async def _remove_broken_connection(self, connection_id: str):
        """
        Remove a broken connection from all tracking.

        Args:
            connection_id: Connection identifier to remove
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Find and remove from session associations
        for session_id, connections in list(self.session_connections.items()):
            if connection_id in connections:
                connections.discard(connection_id)
                if not connections:
                    del self.session_connections[session_id]
                break


# Global connection manager instance
connection_manager = ConnectionManager()


class RecommendationWebSocketHandler:
    """Handles WebSocket communication for AI recommendations."""

    def __init__(self, session_service: SessionService, llm_service: LLMService, context_service: ContextService):
        """
        Initialize WebSocket handler.

        Args:
            session_service: Service for session management
            llm_service: Service for LLM operations
            context_service: Service for managing AI context
        """
        self.session_service = session_service
        self.llm_service = llm_service
        self.context_service = context_service

    async def handle_connection(self, websocket: WebSocket, session_id: str):
        """
        Handle a WebSocket connection for a specific session.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier

        Raises:
            HTTPException: If session is not found or invalid
        """
        # Validate session exists
        session = self.session_service.get_session(session_id)
        if not session:
            await websocket.close(code=4004, reason="Session not found")
            return

        # Generate unique connection ID
        connection_id = f"{session_id}_{id(websocket)}"

        try:
            # Accept connection
            await connection_manager.connect(websocket, session_id, connection_id)

            # Send initial session state
            await self._send_session_state(session, connection_id)

            # Listen for messages
            await self._listen_for_messages(websocket, session_id, connection_id)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for session {session_id}")
        except Exception as e:
            logger.error(f"Error in WebSocket handler for session {session_id}: {e}")
        finally:
            connection_manager.disconnect(connection_id, session_id)

    async def _listen_for_messages(self, websocket: WebSocket, session_id: str, connection_id: str):
        """
        Listen for incoming WebSocket messages.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier
            connection_id: Connection identifier
        """
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    await self._handle_message(message, session_id, connection_id)
                except json.JSONDecodeError:
                    await self._send_error_message("Invalid JSON format", connection_id)
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    await self._send_error_message("Error processing message", connection_id)

        except WebSocketDisconnect:
            raise
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
            raise

    async def _handle_message(self, message: dict, session_id: str, connection_id: str):
        """
        Handle incoming WebSocket message.

        Args:
            message: Parsed JSON message
            session_id: Session identifier
            connection_id: Connection identifier
        """
        message_type = message.get("type")

        if message_type == "request_recommendation":
            await self._handle_recommendation_request(session_id, connection_id)
        elif message_type == "ping":
            await self._handle_ping(connection_id)
        else:
            await self._send_error_message(f"Unknown message type: {message_type}", connection_id)

    async def _handle_recommendation_request(self, session_id: str, connection_id: str):
        """
        Handle request for new AI recommendation.

        Args:
            session_id: Session identifier
            connection_id: Connection identifier
        """
        try:
            # Get current session
            session = self.session_service.get_session(session_id)
            if not session:
                await self._send_error_message("Session not found", connection_id)
                return

            # Check if session can receive recommendations
            if session.status != "active":
                await self._send_error_message("Session is not active", connection_id)
                return

            if len(session.remaining_words) < 4:
                await self._send_error_message("Not enough words remaining", connection_id)
                return

            # Send recommendation request acknowledgment
            await connection_manager.send_personal_message(
                json.dumps({"type": "recommendation_request_received", "timestamp": session.last_activity.isoformat()}),
                connection_id,
            )

            # Get or create context for the session
            context = self.context_service.get_context_for_session(session.id)
            if not context:
                context = self.context_service.create_context_for_session(session)

            # Generate recommendation (this may take some time)
            recommendation = await self.llm_service.generate_recommendation(
                session.id, context, session.llm_model_config
            )

            # Send recommendation to client
            await self._send_recommendation(recommendation, connection_id)

        except Exception as e:
            logger.error(f"Error handling recommendation request: {e}")
            await self._send_error_message("Error generating recommendation", connection_id)

    async def _handle_ping(self, connection_id: str):
        """
        Handle ping message for connection health check.

        Args:
            connection_id: Connection identifier
        """
        await connection_manager.send_personal_message(
            json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}), connection_id
        )

    async def _send_session_state(self, session: Session, connection_id: str):
        """
        Send current session state to client.

        Args:
            session: Session object
            connection_id: Connection identifier
        """
        message = {
            "type": "session_state",
            "data": {
                "session_id": session.id,
                "status": session.status,
                "solved_groups_count": session.solved_groups_count,
                "remaining_words": session.remaining_words,
                "incorrect_evaluation_count": session.incorrect_evaluation_count,
                "pending_recommendation_id": session.pending_recommendation_id,
            },
            "timestamp": session.last_activity.isoformat(),
        }

        await connection_manager.send_personal_message(json.dumps(message), connection_id)

    async def _send_recommendation(self, recommendation: Recommendation, connection_id: str):
        """
        Send new recommendation to client.

        Args:
            recommendation: Recommendation object
            connection_id: Connection identifier
        """
        message = {
            "type": "new_recommendation",
            "data": {
                "id": recommendation.id,
                "session_id": recommendation.session_id,
                "recommended_words": recommendation.recommended_words,
                "explanation": recommendation.explanation,
                "processing_time_ms": recommendation.processing_time_ms,
                "llm_model": recommendation.llm_model,
            },
            "timestamp": recommendation.timestamp.isoformat(),
        }

        await connection_manager.send_personal_message(json.dumps(message), connection_id)

    async def _send_error_message(self, error: str, connection_id: str):
        """
        Send error message to client.

        Args:
            error: Error description
            connection_id: Connection identifier
        """
        message = {"type": "error", "error": error, "timestamp": datetime.now().isoformat()}

        await connection_manager.send_personal_message(json.dumps(message), connection_id)

    async def broadcast_recommendation_update(self, session_id: str, recommendation: Recommendation):
        """
        Broadcast recommendation update to all session connections.

        Args:
            session_id: Session identifier
            recommendation: Updated recommendation
        """
        message = {
            "type": "recommendation_updated",
            "data": {
                "id": recommendation.id,
                "user_evaluation": recommendation.user_evaluation,
                "evaluation_timestamp": (
                    recommendation.evaluation_timestamp.isoformat() if recommendation.evaluation_timestamp else None
                ),
            },
            "timestamp": datetime.now().isoformat(),
        }

        await connection_manager.broadcast_to_session(json.dumps(message), session_id)

    async def broadcast_session_update(self, session: Session):
        """
        Broadcast session state update to all session connections.

        Args:
            session: Updated session
        """
        message = {
            "type": "session_updated",
            "data": {
                "session_id": session.id,
                "status": session.status,
                "solved_groups_count": session.solved_groups_count,
                "remaining_words": session.remaining_words,
                "incorrect_evaluation_count": session.incorrect_evaluation_count,
                "pending_recommendation_id": session.pending_recommendation_id,
            },
            "timestamp": session.last_activity.isoformat(),
        }

        await connection_manager.broadcast_to_session(json.dumps(message), session.session_id)
