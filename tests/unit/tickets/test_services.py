import uuid
from unittest.mock import AsyncMock

import pytest

from flowdesk.modules.tickets.models import (
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
    TicketStatusHistory,
)
from flowdesk.modules.tickets.repositories import (
    TicketCategoryRepository,
    TicketStatusHistoryRepository,
)
from flowdesk.modules.tickets.schemas import (
    TicketCategoryCreateSchema,
    TicketCategoryUpdateSchema,
)
from flowdesk.modules.tickets.services import (
    TicketCategoryService,
    TicketStatusHistoryService,
)
from flowdesk.modules.users.models import User  # noqa: F401


@pytest.mark.asyncio
async def test_category_service_builds_category_from_create_schema() -> None:
    repository = AsyncMock(spec=TicketCategoryRepository)
    repository.create_ticket_category.side_effect = lambda category: category
    service = TicketCategoryService(repository)
    data = TicketCategoryCreateSchema(name="Access", description="Access problems")

    result = await service.create_ticket_category(data)

    assert result.name == "Access"
    assert result.description == "Access problems"
    repository.create_ticket_category.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_category_service_updates_only_provided_fields() -> None:
    repository = AsyncMock(spec=TicketCategoryRepository)
    repository.update_ticket_category.side_effect = lambda category: category
    service = TicketCategoryService(repository)
    category = TicketCategory(id=1, name="Access", description="Old description")

    result = await service.update_ticket_category(
        category,
        TicketCategoryUpdateSchema(description=None),
    )

    assert result.name == "Access"
    assert result.description is None
    repository.update_ticket_category.assert_awaited_once_with(category)


@pytest.mark.asyncio
async def test_status_history_service_changes_ticket_and_records_previous_status() -> None:
    repository = AsyncMock(spec=TicketStatusHistoryRepository)
    repository.create_ticket_status_history.side_effect = lambda history: history
    service = TicketStatusHistoryService(repository)
    ticket = Ticket(
        id=uuid.uuid4(),
        title="Cannot sign in",
        description="Login fails",
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        author_id=uuid.uuid4(),
        ticket_category_id=1,
    )
    changed_by_id = uuid.uuid4()

    result = await service.create_ticket_status_history(
        ticket,
        TicketStatus.IN_PROGRESS,
        changed_by_id,
    )

    assert isinstance(result, TicketStatusHistory)
    assert result.old_status is TicketStatus.OPEN
    assert result.new_status is TicketStatus.IN_PROGRESS
    assert result.changed_by_id == changed_by_id
    assert ticket.status is TicketStatus.IN_PROGRESS
    repository.create_ticket_status_history.assert_awaited_once_with(result)
