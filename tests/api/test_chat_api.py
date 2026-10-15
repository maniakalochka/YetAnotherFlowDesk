import datetime
import uuid
from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from flowdesk.dependencies.chat import get_ticket_chat_service
from flowdesk.dependencies.ticket import get_ticket_service, get_ws_ticket
from flowdesk.dependencies.user import get_current_user, get_ws_current_user
from flowdesk.main import app
from flowdesk.modules.chat.manager import manager
from flowdesk.modules.chat.models import TicketChatMessage
from flowdesk.modules.chat.services import TicketChatService
from flowdesk.modules.tickets.models import Ticket, TicketPriority, TicketStatus
from flowdesk.modules.tickets.services import TicketService
from flowdesk.modules.users.models import User, UserRole


@pytest.fixture
def client() -> Generator[TestClient]:
    manager.active_connections.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    manager.active_connections.clear()


def make_user(role: UserRole = UserRole.USER) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{uuid.uuid4()}@example.com",
        hashed_password="hashed-password",
        fname="John",
        lname="Doe",
        role=role,
        is_active=True,
    )


def make_ticket(author_id: uuid.UUID) -> Ticket:
    return Ticket(
        id=uuid.uuid4(),
        title="Cannot sign in",
        description="Login fails",
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        archived=False,
        author_id=author_id,
        ticket_category_id=1,
    )


def make_message(ticket_id: uuid.UUID, author_id: uuid.UUID, text: str) -> TicketChatMessage:
    timestamp = datetime.datetime.now(datetime.UTC)
    return TicketChatMessage(
        id=uuid.uuid4(),
        text=text,
        ticket_id=ticket_id,
        author_id=author_id,
        created_at=timestamp,
        updated_at=timestamp,
    )


def override_websocket_dependencies(
    user: User,
    ticket: Ticket,
    chat_service: TicketChatService,
) -> None:
    app.dependency_overrides[get_ws_current_user] = lambda: user
    app.dependency_overrides[get_ws_ticket] = lambda: ticket
    app.dependency_overrides[get_ticket_chat_service] = lambda: chat_service


def test_websocket_persists_and_broadcasts_valid_message(client: TestClient) -> None:
    user = make_user()
    ticket = make_ticket(user.id)
    message = make_message(ticket.id, user.id, "Hello")
    chat_service = AsyncMock(spec=TicketChatService)
    chat_service.create_message.return_value = message
    override_websocket_dependencies(user, ticket, chat_service)

    with client.websocket_connect(f"/tickets/{ticket.id}/ws") as websocket:
        websocket.send_json({"content": "  Hello  "})
        response = websocket.receive_json()

    assert response == {
        "event": "new_message",
        "id": str(message.id),
        "ticket_id": str(ticket.id),
        "author_id": str(user.id),
        "content": "Hello",
        "created_at": message.created_at.isoformat().replace("+00:00", "Z"),
    }
    data = chat_service.create_message.await_args.args[0]
    assert data.content == "Hello"
    chat_service.create_message.assert_awaited_once_with(
        data,
        ticket_id=ticket.id,
        author_id=user.id,
    )
    assert ticket.id not in manager.active_connections


def test_websocket_rejects_blank_message_without_persisting(client: TestClient) -> None:
    user = make_user()
    ticket = make_ticket(user.id)
    chat_service = AsyncMock(spec=TicketChatService)
    override_websocket_dependencies(user, ticket, chat_service)

    with client.websocket_connect(f"/tickets/{ticket.id}/ws") as websocket:
        websocket.send_json({"content": "   "})
        response = websocket.receive_json()

    assert response["event"] == "error"
    assert response["detail"] == "Invalid message"
    chat_service.create_message.assert_not_awaited()


def test_websocket_rejects_invalid_json_without_persisting(client: TestClient) -> None:
    user = make_user()
    ticket = make_ticket(user.id)
    chat_service = AsyncMock(spec=TicketChatService)
    override_websocket_dependencies(user, ticket, chat_service)

    with client.websocket_connect(f"/tickets/{ticket.id}/ws") as websocket:
        websocket.send_text("not-json")
        response = websocket.receive_json()

    assert response == {"event": "error", "detail": "Invalid JSON"}
    chat_service.create_message.assert_not_awaited()


def test_websocket_rejects_connection_without_token(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect) as error:
        with client.websocket_connect(f"/tickets/{uuid.uuid4()}/ws"):
            pass

    assert error.value.code == 1008


def test_websocket_rejects_access_to_another_users_ticket(client: TestClient) -> None:
    user = make_user()
    ticket = make_ticket(uuid.uuid4())
    ticket_service = AsyncMock(spec=TicketService)
    ticket_service.get_ticket_by_id.return_value = ticket
    chat_service = AsyncMock(spec=TicketChatService)
    app.dependency_overrides[get_ws_current_user] = lambda: user
    app.dependency_overrides[get_ticket_service] = lambda: ticket_service
    app.dependency_overrides[get_ticket_chat_service] = lambda: chat_service

    with pytest.raises(WebSocketDisconnect) as error:
        with client.websocket_connect(f"/tickets/{ticket.id}/ws"):
            pass

    assert error.value.code == 1008
    chat_service.create_message.assert_not_awaited()


def test_ticket_owner_can_read_message_history(client: TestClient) -> None:
    user = make_user()
    ticket = make_ticket(user.id)
    message = make_message(ticket.id, user.id, "Hello")
    ticket_service = AsyncMock(spec=TicketService)
    ticket_service.get_ticket_by_id.return_value = ticket
    chat_service = AsyncMock(spec=TicketChatService)
    chat_service.get_message_history.return_value = [message]
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_ticket_service] = lambda: ticket_service
    app.dependency_overrides[get_ticket_chat_service] = lambda: chat_service

    response = client.get(f"/tickets/{ticket.id}/messages")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(message.id),
            "ticket_id": str(ticket.id),
            "author_id": str(user.id),
            "content": "Hello",
            "created_at": message.created_at.isoformat().replace("+00:00", "Z"),
        }
    ]
    chat_service.get_message_history.assert_awaited_once_with(ticket.id)


def test_message_history_requires_authentication(client: TestClient) -> None:
    response = client.get(f"/tickets/{uuid.uuid4()}/messages")

    assert response.status_code == 401


def test_regular_user_cannot_read_another_ticket_messages(client: TestClient) -> None:
    user = make_user()
    ticket = make_ticket(uuid.uuid4())
    ticket_service = AsyncMock(spec=TicketService)
    ticket_service.get_ticket_by_id.return_value = ticket
    chat_service = AsyncMock(spec=TicketChatService)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_ticket_service] = lambda: ticket_service
    app.dependency_overrides[get_ticket_chat_service] = lambda: chat_service

    response = client.get(f"/tickets/{ticket.id}/messages")

    assert response.status_code == 403
    chat_service.get_message_history.assert_not_awaited()


def test_missing_ticket_message_history_returns_not_found(client: TestClient) -> None:
    user = make_user()
    ticket_id = uuid.uuid4()
    ticket_service = AsyncMock(spec=TicketService)
    ticket_service.get_ticket_by_id.return_value = None
    chat_service = AsyncMock(spec=TicketChatService)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_ticket_service] = lambda: ticket_service
    app.dependency_overrides[get_ticket_chat_service] = lambda: chat_service

    response = client.get(f"/tickets/{ticket_id}/messages")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"
    chat_service.get_message_history.assert_not_awaited()
