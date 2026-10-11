import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from flowdesk.dependencies.permissions import SupportOrAdminDep
from flowdesk.dependencies.ticket import get_ticket_service
from flowdesk.dependencies.user import CurrentUserDep
from flowdesk.modules.tickets.schemas import TicketCreateSchema, TicketSchema, TicketUpdateSchema
from flowdesk.modules.tickets.services import TicketService
from flowdesk.modules.users.models import UserRole

tickets_router = APIRouter(tags=["tickets"])


@tickets_router.get("/tickets/{ticket_id}")
async def get_ticket(
    ticket_id: uuid.UUID,
    current_user: CurrentUserDep,
    ticket_service: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketSchema:
    ticket = await ticket_service.get_ticket_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role == UserRole.USER and ticket.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this ticket",
        )
    return TicketSchema.model_validate(ticket)


@tickets_router.post("/tickets")
async def create_ticket(
    ticket: TicketCreateSchema,
    ticket_service: Annotated[TicketService, Depends(get_ticket_service)],
    current_user: CurrentUserDep,
) -> TicketCreateSchema:
    created_ticket = await ticket_service.create_ticket(ticket, author_id=current_user.id)
    return TicketCreateSchema.model_validate(created_ticket)


@tickets_router.patch("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: uuid.UUID,
    ticket_data: TicketUpdateSchema,
    ticket_service: Annotated[TicketService, Depends(get_ticket_service)],
    current_user: Annotated[SupportOrAdminDep, Depends(SupportOrAdminDep)],
) -> TicketSchema:
    existing_ticket = await ticket_service.get_ticket_by_id(ticket_id)

    if existing_ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    if existing_ticket.archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update an archived ticket",
        )
    updated_ticket = await ticket_service.update_ticket(ticket_id, ticket_data)

    return TicketSchema.model_validate(updated_ticket)


@tickets_router.delete(
    "/tickets/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ticket(
    ticket_id: uuid.UUID,
    ticket_service: Annotated[TicketService, Depends(get_ticket_service)],
    current_user: SupportOrAdminDep,
) -> None:
    existing_ticket = await ticket_service.get_ticket_by_id(ticket_id)

    if existing_ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    if existing_ticket.archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete an archived ticket",
        )

    await ticket_service.delete_ticket(existing_ticket)
