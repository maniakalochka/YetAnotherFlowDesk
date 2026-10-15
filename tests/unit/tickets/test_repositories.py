import uuid
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.modules.tickets.models import TicketCategory, TicketStatus, TicketStatusHistory
from flowdesk.modules.tickets.repositories import (
    TicketCategoryRepository,
    TicketStatusHistoryRepository,
)
from flowdesk.modules.users.models import User  # noqa: F401


@pytest.mark.asyncio
async def test_category_repository_lists_categories_in_stable_name_order() -> None:
    session = AsyncMock(spec=AsyncSession)
    scalar_result = Mock()
    categories = [TicketCategory(id=1, name="Access", description=None)]
    scalar_result.all.return_value = categories
    session.scalars.return_value = scalar_result
    repository = TicketCategoryRepository(session)

    result = await repository.get_all_ticket_categories()

    assert result == categories
    statement = session.scalars.await_args.args[0]
    assert str(statement).endswith(
        "FROM ticket_categories ORDER BY ticket_categories.name, ticket_categories.id"
    )


@pytest.mark.asyncio
async def test_category_repository_creates_and_refreshes_category() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = TicketCategoryRepository(session)
    category = TicketCategory(name="Access", description="Access problems")

    result = await repository.create_ticket_category(category)

    assert result is category
    session.add.assert_called_once_with(category)
    session.commit.assert_awaited_once_with()
    session.refresh.assert_awaited_once_with(category)


@pytest.mark.asyncio
async def test_category_repository_deletes_category() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = TicketCategoryRepository(session)
    category = TicketCategory(id=1, name="Access", description=None)

    await repository.delete_ticket_category(category)

    session.delete.assert_awaited_once_with(category)
    session.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_status_history_repository_lists_entries_chronologically() -> None:
    session = AsyncMock(spec=AsyncSession)
    scalar_result = Mock()
    history = [
        TicketStatusHistory(
            id=uuid.uuid4(),
            ticket_id=uuid.uuid4(),
            old_status=TicketStatus.OPEN,
            new_status=TicketStatus.IN_PROGRESS,
            changed_by_id=uuid.uuid4(),
        )
    ]
    scalar_result.all.return_value = history
    session.scalars.return_value = scalar_result
    repository = TicketStatusHistoryRepository(session)
    ticket_id = uuid.uuid4()

    result = await repository.get_ticket_status_history_by_ticket_id(ticket_id)

    assert result == history
    statement = session.scalars.await_args.args[0]
    assert str(statement).endswith(
        "WHERE ticket_status_history.ticket_id = :ticket_id_1 "
        "ORDER BY ticket_status_history.created_at, ticket_status_history.id"
    )
    assert statement.compile().params["ticket_id_1"] == ticket_id


@pytest.mark.asyncio
async def test_status_history_repository_persists_and_refreshes_entry() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = TicketStatusHistoryRepository(session)
    history = TicketStatusHistory(
        ticket_id=uuid.uuid4(),
        old_status=TicketStatus.OPEN,
        new_status=TicketStatus.IN_PROGRESS,
        changed_by_id=uuid.uuid4(),
    )

    result = await repository.create_ticket_status_history(history)

    assert result is history
    session.add.assert_called_once_with(history)
    session.commit.assert_awaited_once_with()
    session.refresh.assert_awaited_once_with(history)
