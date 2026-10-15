import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import WebSocket

from flowdesk.modules.chat.manager import ConnectionManager


def test_disconnect_is_idempotent() -> None:
    manager = ConnectionManager()
    ticket_id = uuid.uuid4()
    websocket = AsyncMock(spec=WebSocket)
    manager.active_connections[ticket_id] = {websocket}

    manager.disconnect(ticket_id, websocket)
    manager.disconnect(ticket_id, websocket)

    assert ticket_id not in manager.active_connections


@pytest.mark.asyncio
async def test_broadcast_removes_broken_connection() -> None:
    manager = ConnectionManager()
    ticket_id = uuid.uuid4()
    websocket = AsyncMock(spec=WebSocket)
    websocket.send_json.side_effect = RuntimeError
    manager.active_connections[ticket_id] = {websocket}

    await manager.broadcast(ticket_id, {"event": "new_message"})

    assert ticket_id not in manager.active_connections
