import uuid
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.modules.chat.models import TicketChatMessage
from flowdesk.modules.chat.repositories import TicketChatRepository
from flowdesk.modules.users.models import User  # noqa: F401


def make_message() -> TicketChatMessage:
    return TicketChatMessage(
        id=uuid.uuid4(),
        text="A message",
        ticket_id=uuid.uuid4(),
        author_id=uuid.uuid4(),
    )


@pytest.mark.asyncio
async def test_get_ticket_chat_messages_filters_and_orders_chronologically() -> None:
    session = AsyncMock(spec=AsyncSession)
    scalar_result = Mock()
    messages = [make_message(), make_message()]
    scalar_result.all.return_value = messages
    session.scalars.return_value = scalar_result
    repository = TicketChatRepository(session)
    ticket_id = uuid.uuid4()

    result = await repository.get_ticket_chat_messages_by_ticket_id(ticket_id)

    assert result == messages
    statement = session.scalars.await_args.args[0]
    assert str(statement).endswith(
        "WHERE ticket_messages.ticket_id = :ticket_id_1 "
        "ORDER BY ticket_messages.created_at, ticket_messages.id"
    )
    assert statement.compile().params["ticket_id_1"] == ticket_id


@pytest.mark.asyncio
async def test_create_ticket_chat_message_persists_and_refreshes_message() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = TicketChatRepository(session)
    message = make_message()

    result = await repository.create_ticket_chat_message(message)

    assert result is message
    session.add.assert_called_once_with(message)
    session.commit.assert_awaited_once_with()
    session.refresh.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_update_ticket_chat_message_updates_all_mutable_columns() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = TicketChatRepository(session)
    message = make_message()

    result = await repository.update_ticket_chat_message(message)

    assert result is message
    statement = session.execute.await_args.args[0]
    params = statement.compile().params
    assert params["text"] == message.text
    assert params["ticket_id"] == message.ticket_id
    assert params["author_id"] == message.author_id
    assert params["id_1"] == message.id
    session.commit.assert_awaited_once_with()
    session.refresh.assert_awaited_once_with(message)
