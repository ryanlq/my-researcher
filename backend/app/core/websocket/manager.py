"""WebSocket Connection Manager"""

from fastapi import WebSocket
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections for real-time progress updates
    """

    def __init__(self):
        # Active connections: {research_id: [websockets]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, research_id: int):
        """
        Accept and register a new WebSocket connection
        """
        await websocket.accept()

        if research_id not in self.active_connections:
            self.active_connections[research_id] = []

        self.active_connections[research_id].append(websocket)
        logger.info(f"WebSocket connected for research {research_id}")

    def disconnect(self, websocket: WebSocket, research_id: int):
        """
        Remove a WebSocket connection
        """
        if research_id in self.active_connections:
            if websocket in self.active_connections[research_id]:
                self.active_connections[research_id].remove(websocket)

            # Clean up empty lists
            if not self.active_connections[research_id]:
                del self.active_connections[research_id]

        logger.info(f"WebSocket disconnected for research {research_id}")

    async def send_message(self, websocket: WebSocket, message: dict):
        """
        Send a message to a specific WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")

    async def broadcast_progress(self, research_id: int, data: dict):
        """
        Broadcast progress update to all connections for a research
        """
        if research_id not in self.active_connections:
            return

        message = {
            "event": "research.progress",
            "research_id": research_id,
            "data": data
        }

        # Send to all connected websockets for this research
        disconnected = []
        for websocket in self.active_connections[research_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")
                disconnected.append(websocket)

        # Remove disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket, research_id)

    async def send_error(self, websocket: WebSocket, research_id: int, error: str):
        """
        Send error message to a specific WebSocket
        """
        message = {
            "event": "research.error",
            "research_id": research_id,
            "error": error
        }
        await self.send_message(websocket, message)

    async def broadcast_started(self, research_id: int, estimated_time_minutes: int):
        """
        Broadcast research started event
        """
        message = {
            "event": "research.started",
            "research_id": research_id,
            "estimated_time_minutes": estimated_time_minutes
        }
        await self.broadcast_to_research(research_id, message)

    async def broadcast_completed(self, research_id: int, report: str):
        """
        Broadcast research completed event
        """
        message = {
            "event": "research.completed",
            "research_id": research_id,
            "report": report
        }
        await self.broadcast_to_research(research_id, message)

    async def broadcast_stage(self, research_id: int, stage: str, message: str):
        """
        Broadcast research stage change
        """
        data = {
            "stage": stage,
            "message": message
        }
        await self.broadcast_progress(research_id, data)

    async def broadcast_to_research(self, research_id: int, message: dict):
        """
        Broadcast a message to all connections for a research
        """
        if research_id not in self.active_connections:
            return

        disconnected = []
        for websocket in self.active_connections[research_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                disconnected.append(websocket)

        # Remove disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket, research_id)

    def get_connection_count(self, research_id: int) -> int:
        """
        Get number of active connections for a research
        """
        if research_id not in self.active_connections:
            return 0
        return len(self.active_connections[research_id])


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
