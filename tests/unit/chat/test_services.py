import uuid
from unittest.mock import AsyncMock

import pytest

from flowdesk.modules.chat.models import TicketChatMessage
from flowdesk.modules.chat.repositories import TicketChatRepository
from flowdesk.modules.chat.schemas import TicketChatMessageCreateSchema
from flowdesk.modules.chat.services import TicketChatService
from flowdesk.modules.users.models import User  # noqa: F401


@pytest.mark.asyncio
async def test_create_message_builds_and_persists_chat_message() -> None:
    repository = AsyncMock(spec=TicketChatRepository)
    repository.create_ticket_chat_message.side_effect = lambda message: message
    service = TicketChatService(repository)
    ticket_id = uuid.uuid4()
    author_id = uuid.uuid4()
    data = TicketChatMessageCreateSchema(content="Hello")

    result = await service.create_message(
        data,
        ticket_id=ticket_id,
        author_id=author_id,
    )

    assert isinstance(result, TicketChatMessage)
    assert result.text == "Hello"
    assert result.ticket_id == ticket_id
    assert result.author_id == author_id
    repository.create_ticket_chat_message.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_get_message_history_delegates_to_repository() -> None:
    repository = AsyncMock(spec=TicketChatRepository)
    service = TicketChatService(repository)
    ticket_id = uuid.uuid4()
    messages = [
        TicketChatMessage(
            id=uuid.uuid4(),
            text="Hello",
            ticket_id=ticket_id,
            author_id=uuid.uuid4(),
        )
    ]
    repository.get_ticket_chat_messages_by_ticket_id.return_value = messages

    result = await service.get_message_history(ticket_id)

    assert result == messages
    repository.get_ticket_chat_messages_by_ticket_id.assert_awaited_once_with(ticket_id)
