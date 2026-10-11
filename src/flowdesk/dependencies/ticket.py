from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.dependencies.database import get_async_session
from flowdesk.modules.tickets.repositories import (
    TicketCommentRepository,
    TicketRepository,
    TicketStatusHistoryRepository,
)
from flowdesk.modules.tickets.services import (
    TicketCommentService,
    TicketService,
    TicketStatusHistoryService,
)


def get_ticket_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TicketRepository:
    return TicketRepository(session)


def get_ticket_service(
    repository: Annotated[TicketRepository, Depends(get_ticket_repository)],
) -> TicketService:
    return TicketService(repository)


def get_ticket_status_history_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TicketStatusHistoryRepository:
    return TicketStatusHistoryRepository(session)


def get_ticket_status_history_service(
    repository: Annotated[
        TicketStatusHistoryRepository, Depends(get_ticket_status_history_repository)
    ],
) -> TicketStatusHistoryService:
    return TicketStatusHistoryService(repository)


def get_ticket_comment_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TicketCommentRepository:
    return TicketCommentRepository(session)


def get_ticket_comment_service(
    repository: Annotated[TicketCommentRepository, Depends(get_ticket_comment_repository)],
) -> TicketCommentService:
    return TicketCommentService(repository)


def get_ticket_category_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TicketCommentRepository:
    return TicketCommentRepository(session)


def get_ticket_category_service(
    repository: Annotated[TicketCommentRepository, Depends(get_ticket_category_repository)],
) -> TicketCommentService:
    return TicketCommentService(repository)
