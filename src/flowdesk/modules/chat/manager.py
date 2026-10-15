import uuid
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[uuid.UUID, set[WebSocket]] = {}

    async def connect(self, ticket_id: uuid.UUID, ws: WebSocket) -> None:
        await ws.accept()

        if ticket_id not in self.active_connections:
            self.active_connections[ticket_id] = set()
        self.active_connections[ticket_id].add(ws)

    def disconnect(self, ticket_id: uuid.UUID, ws: WebSocket) -> None:
        connections = self.active_connections.get(ticket_id)
        if connections is None:
            return

        connections.discard(ws)
        if not connections:
            self.active_connections.pop(ticket_id, None)

    async def broadcast(self, ticket_id: uuid.UUID, message: dict[str, Any]) -> None:
        connections = self.active_connections.get(ticket_id, set())
        for ws in tuple(connections):
            try:
                await ws.send_json(message)
            except (RuntimeError, OSError):
                self.disconnect(ticket_id, ws)


manager = ConnectionManager()
