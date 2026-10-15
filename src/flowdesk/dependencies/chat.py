from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.dependencies.database import get_async_session
from flowdesk.modules.chat.repositories import TicketChatRepository
from flowdesk.modules.chat.services import TicketChatService


def get_ticket_chat_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TicketChatRepository:
    return TicketChatRepository(session)


def get_ticket_chat_service(
    repository: Annotated[
        TicketChatRepository,
        Depends(get_ticket_chat_repository),
    ],
) -> TicketChatService:
    return TicketChatService(repository)


TicketChatServiceDep = Annotated[
    TicketChatService,
    Depends(get_ticket_chat_service),
]
