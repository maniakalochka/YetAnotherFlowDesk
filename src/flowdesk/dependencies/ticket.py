import uuid
from typing import Annotated

from fastapi import Depends, WebSocketException, status
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.dependencies.database import get_async_session
from flowdesk.dependencies.user import WsCurrentUserDep
from flowdesk.modules.tickets.models import Ticket
from flowdesk.modules.tickets.repositories import (
    TicketCategoryRepository,
    TicketRepository,
    TicketStatusHistoryRepository,
)
from flowdesk.modules.tickets.services import (
    TicketCategoryService,
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


def get_ticket_category_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TicketCategoryRepository:
    return TicketCategoryRepository(session)


def get_ticket_category_service(
    repository: Annotated[TicketCategoryRepository, Depends(get_ticket_category_repository)],
) -> TicketCategoryService:
    return TicketCategoryService(repository)


TicketServiceDep = Annotated[TicketService, Depends(get_ticket_service)]
TicketCategoryServiceDep = Annotated[
    TicketCategoryService,
    Depends(get_ticket_category_service),
]
TicketStatusHistoryServiceDep = Annotated[
    TicketStatusHistoryService,
    Depends(get_ticket_status_history_service),
]


async def get_ws_ticket(
    ticket_id: uuid.UUID,
    current_user: WsCurrentUserDep,
    ticket_service: Annotated[TicketService, Depends(get_ticket_service)],
) -> Ticket:
    ticket = await ticket_service.get_ticket_by_id(ticket_id)

    if ticket is None:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Ticket not found",
        )

    if ticket.archived:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Cannot access an archived ticket",
        )

    if current_user.role not in ["admin", "support"] and ticket.author_id != current_user.id:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="You do not have permission to access this ticket",
        )

    return ticket


WsTicketDep = Annotated[Ticket, Depends(get_ws_ticket)]
