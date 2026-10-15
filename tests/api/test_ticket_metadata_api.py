import datetime
import uuid
from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from flowdesk.dependencies.ticket import (
    get_ticket_category_service,
    get_ticket_service,
    get_ticket_status_history_service,
)
from flowdesk.dependencies.user import get_current_user
from flowdesk.main import app
from flowdesk.modules.tickets.models import (
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
    TicketStatusHistory,
)
from flowdesk.modules.tickets.services import (
    TicketCategoryService,
    TicketService,
    TicketStatusHistoryService,
)
from flowdesk.modules.users.models import User, UserRole


@pytest.fixture
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


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


def make_category() -> TicketCategory:
    timestamp = datetime.datetime.now(datetime.UTC)
    return TicketCategory(
        id=1,
        name="Access",
        description="Access problems",
        created_at=timestamp,
        updated_at=timestamp,
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


def make_history(ticket_id: uuid.UUID, changed_by_id: uuid.UUID) -> TicketStatusHistory:
    return TicketStatusHistory(
        id=uuid.uuid4(),
        ticket_id=ticket_id,
        old_status=TicketStatus.OPEN,
        new_status=TicketStatus.IN_PROGRESS,
        changed_by_id=changed_by_id,
        created_at=datetime.datetime.now(datetime.UTC),
    )


def test_authenticated_user_can_list_ticket_categories(client: TestClient) -> None:
    user = make_user()
    category = make_category()
    service = AsyncMock(spec=TicketCategoryService)
    service.get_ticket_categories.return_value = [category]
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_ticket_category_service] = lambda: service

    response = client.get("/ticket-categories")

    assert response.status_code == 200
    assert response.json()[0]["name"] == category.name


def test_admin_can_create_ticket_category(client: TestClient) -> None:
    admin = make_user(UserRole.ADMIN)
    category = make_category()
    service = AsyncMock(spec=TicketCategoryService)
    service.create_ticket_category.return_value = category
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[get_ticket_category_service] = lambda: service

    response = client.post(
        "/ticket-categories",
        json={"name": category.name, "description": category.description},
    )

    assert response.status_code == 201
    assert response.json()["id"] == category.id
    service.create_ticket_category.assert_awaited_once()


def test_regular_user_cannot_create_ticket_category(client: TestClient) -> None:
    user = make_user()
    service = AsyncMock(spec=TicketCategoryService)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_ticket_category_service] = lambda: service

    response = client.post(
        "/ticket-categories",
        json={"name": "Access", "description": None},
    )

    assert response.status_code == 403
    service.create_ticket_category.assert_not_awaited()


def test_ticket_owner_can_read_status_history(client: TestClient) -> None:
    user = make_user()
    ticket = make_ticket(user.id)
    history = make_history(ticket.id, uuid.uuid4())
    ticket_service = AsyncMock(spec=TicketService)
    ticket_service.get_ticket_by_id.return_value = ticket
    history_service = AsyncMock(spec=TicketStatusHistoryService)
    history_service.get_ticket_status_history_by_ticket_id.return_value = [history]
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_ticket_service] = lambda: ticket_service
    app.dependency_overrides[get_ticket_status_history_service] = lambda: history_service

    response = client.get(f"/tickets/{ticket.id}/status-history")

    assert response.status_code == 200
    assert response.json()[0]["old_status"] == TicketStatus.OPEN
    assert response.json()[0]["new_status"] == TicketStatus.IN_PROGRESS


def test_regular_user_cannot_read_another_ticket_status_history(client: TestClient) -> None:
    user = make_user()
    ticket = make_ticket(uuid.uuid4())
    ticket_service = AsyncMock(spec=TicketService)
    ticket_service.get_ticket_by_id.return_value = ticket
    history_service = AsyncMock(spec=TicketStatusHistoryService)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_ticket_service] = lambda: ticket_service
    app.dependency_overrides[get_ticket_status_history_service] = lambda: history_service

    response = client.get(f"/tickets/{ticket.id}/status-history")

    assert response.status_code == 403
    history_service.get_ticket_status_history_by_ticket_id.assert_not_awaited()


def test_support_can_change_ticket_status_and_create_history(client: TestClient) -> None:
    support = make_user(UserRole.SUPPORT)
    ticket = make_ticket(uuid.uuid4())
    history = make_history(ticket.id, support.id)
    ticket_service = AsyncMock(spec=TicketService)
    ticket_service.get_ticket_by_id.return_value = ticket
    history_service = AsyncMock(spec=TicketStatusHistoryService)
    history_service.create_ticket_status_history.return_value = history
    app.dependency_overrides[get_current_user] = lambda: support
    app.dependency_overrides[get_ticket_service] = lambda: ticket_service
    app.dependency_overrides[get_ticket_status_history_service] = lambda: history_service

    response = client.patch(
        f"/tickets/{ticket.id}/status",
        json={"status": TicketStatus.IN_PROGRESS},
    )

    assert response.status_code == 200
    assert response.json()["new_status"] == TicketStatus.IN_PROGRESS
    history_service.create_ticket_status_history.assert_awaited_once_with(
        ticket,
        TicketStatus.IN_PROGRESS,
        support.id,
    )
