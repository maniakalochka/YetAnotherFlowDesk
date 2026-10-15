import uuid

from fastapi import APIRouter, HTTPException, status

from flowdesk.dependencies.permissions import SupportOrAdminDep
from flowdesk.dependencies.ticket import (
    TicketCategoryServiceDep,
    TicketServiceDep,
    TicketStatusHistoryServiceDep,
)
from flowdesk.dependencies.user import CurrentAdminDep, CurrentUserDep
from flowdesk.modules.tickets.exceptions import (
    TicketCategoryAlreadyExistsError,
    TicketCategoryInUseError,
)
from flowdesk.modules.tickets.models import Ticket
from flowdesk.modules.tickets.schemas import (
    TicketCategoryCreateSchema,
    TicketCategorySchema,
    TicketCategoryUpdateSchema,
    TicketCreateSchema,
    TicketSchema,
    TicketStatusHistorySchema,
    TicketStatusUpdateSchema,
    TicketUpdateSchema,
)
from flowdesk.modules.users.models import User, UserRole

tickets_router = APIRouter(tags=["tickets"])


def ensure_ticket_access(ticket: Ticket, current_user: User) -> None:
    if current_user.role is UserRole.USER and ticket.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this ticket",
        )


@tickets_router.get("/tickets/{ticket_id}")
async def get_ticket(
    ticket_id: uuid.UUID,
    current_user: CurrentUserDep,
    ticket_service: TicketServiceDep,
) -> TicketSchema:
    ticket = await ticket_service.get_ticket_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ensure_ticket_access(ticket, current_user)
    return TicketSchema.model_validate(ticket)


@tickets_router.post(
    "/tickets",
    response_model=TicketSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(
    ticket: TicketCreateSchema,
    ticket_service: TicketServiceDep,
    current_user: CurrentUserDep,
) -> TicketSchema:
    created_ticket = await ticket_service.create_ticket(ticket, author_id=current_user.id)
    return TicketSchema.model_validate(created_ticket)


@tickets_router.patch("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: uuid.UUID,
    ticket_data: TicketUpdateSchema,
    ticket_service: TicketServiceDep,
    current_user: SupportOrAdminDep,
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
    ticket_service: TicketServiceDep,
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


@tickets_router.get(
    "/ticket-categories",
    response_model=list[TicketCategorySchema],
)
async def list_ticket_categories(
    _: CurrentUserDep,
    category_service: TicketCategoryServiceDep,
) -> list[TicketCategorySchema]:
    categories = await category_service.get_ticket_categories()
    return [TicketCategorySchema.model_validate(category) for category in categories]


@tickets_router.get(
    "/ticket-categories/{category_id}",
    response_model=TicketCategorySchema,
)
async def get_ticket_category(
    category_id: int,
    _: CurrentUserDep,
    category_service: TicketCategoryServiceDep,
) -> TicketCategorySchema:
    category = await category_service.get_ticket_category_by_id(category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket category not found",
        )
    return TicketCategorySchema.model_validate(category)


@tickets_router.post(
    "/ticket-categories",
    response_model=TicketCategorySchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket_category(
    data: TicketCategoryCreateSchema,
    _: CurrentAdminDep,
    category_service: TicketCategoryServiceDep,
) -> TicketCategorySchema:
    try:
        category = await category_service.create_ticket_category(data)
    except TicketCategoryAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket category with this name already exists",
        ) from None
    return TicketCategorySchema.model_validate(category)


@tickets_router.patch(
    "/ticket-categories/{category_id}",
    response_model=TicketCategorySchema,
)
async def update_ticket_category(
    category_id: int,
    data: TicketCategoryUpdateSchema,
    _: CurrentAdminDep,
    category_service: TicketCategoryServiceDep,
) -> TicketCategorySchema:
    category = await category_service.get_ticket_category_by_id(category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket category not found",
        )
    try:
        updated_category = await category_service.update_ticket_category(category, data)
    except TicketCategoryAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket category with this name already exists",
        ) from None
    return TicketCategorySchema.model_validate(updated_category)


@tickets_router.delete(
    "/ticket-categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ticket_category(
    category_id: int,
    _: CurrentAdminDep,
    category_service: TicketCategoryServiceDep,
) -> None:
    category = await category_service.get_ticket_category_by_id(category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket category not found",
        )
    try:
        await category_service.delete_ticket_category(category)
    except TicketCategoryInUseError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket category is used by existing tickets",
        ) from None


@tickets_router.get(
    "/tickets/{ticket_id}/status-history",
    response_model=list[TicketStatusHistorySchema],
)
async def get_ticket_status_history(
    ticket_id: uuid.UUID,
    current_user: CurrentUserDep,
    ticket_service: TicketServiceDep,
    history_service: TicketStatusHistoryServiceDep,
) -> list[TicketStatusHistorySchema]:
    ticket = await ticket_service.get_ticket_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    ensure_ticket_access(ticket, current_user)
    history = await history_service.get_ticket_status_history_by_ticket_id(ticket_id)
    return [TicketStatusHistorySchema.model_validate(item) for item in history]


@tickets_router.patch(
    "/tickets/{ticket_id}/status",
    response_model=TicketStatusHistorySchema,
)
async def change_ticket_status(
    ticket_id: uuid.UUID,
    data: TicketStatusUpdateSchema,
    current_user: SupportOrAdminDep,
    ticket_service: TicketServiceDep,
    history_service: TicketStatusHistoryServiceDep,
) -> TicketStatusHistorySchema:
    ticket = await ticket_service.get_ticket_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    if ticket.archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change the status of an archived ticket",
        )
    if ticket.status is data.status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket already has this status",
        )

    history = await history_service.create_ticket_status_history(
        ticket,
        data.status,
        current_user.id,
    )
    return TicketStatusHistorySchema.model_validate(history)
