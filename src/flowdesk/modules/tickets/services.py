import uuid
from collections.abc import Sequence

from flowdesk.modules.tickets.models import (
    Ticket,
    TicketCategory,
    TicketStatus,
    TicketStatusHistory,
)
from flowdesk.modules.tickets.repositories import (
    TicketCategoryRepository,
    TicketRepository,
    TicketStatusHistoryRepository,
)
from flowdesk.modules.tickets.schemas import (
    TicketCategoryCreateSchema,
    TicketCategoryUpdateSchema,
    TicketCreateSchema,
    TicketUpdateSchema,
)


class TicketService:
    def __init__(self, ticket_repository: TicketRepository):
        self.ticket_repository = ticket_repository

    async def get_ticket_by_id(self, ticket_id: uuid.UUID) -> Ticket | None:
        return await self.ticket_repository.get_ticket_by_id(ticket_id)

    async def create_ticket(self, data: TicketCreateSchema, author_id: uuid.UUID) -> Ticket:
        ticket = Ticket(**data.model_dump(), author_id=author_id)
        return await self.ticket_repository.create_ticket(ticket, author_id)

    async def update_ticket(
        self, ticket_id: uuid.UUID, ticket_data: TicketUpdateSchema
    ) -> Ticket | None:
        return await self.ticket_repository.update_ticket(ticket_id, ticket_data)

    async def delete_ticket(self, ticket: Ticket) -> None:
        await self.ticket_repository.delete_ticket(ticket)

    async def list_tickets(self, skip: int = 0, limit: int = 100) -> Sequence[Ticket]:
        return await self.ticket_repository.list_tickets(skip=skip, limit=limit)


class TicketStatusHistoryService:
    def __init__(
        self,
        ticket_status_history_repository: TicketStatusHistoryRepository,
    ) -> None:
        self.ticket_status_history_repository = ticket_status_history_repository

    async def create_ticket_status_history(
        self,
        ticket: Ticket,
        new_status: TicketStatus,
        changed_by_id: uuid.UUID,
    ) -> TicketStatusHistory:
        history = TicketStatusHistory(
            ticket_id=ticket.id,
            old_status=ticket.status,
            new_status=new_status,
            changed_by_id=changed_by_id,
        )
        ticket.status = new_status
        return await self.ticket_status_history_repository.create_ticket_status_history(history)

    async def get_ticket_status_history_by_ticket_id(
        self, ticket_id: uuid.UUID
    ) -> Sequence[TicketStatusHistory]:
        return await self.ticket_status_history_repository.get_ticket_status_history_by_ticket_id(
            ticket_id
        )


class TicketCategoryService:
    def __init__(self, ticket_category_repository: TicketCategoryRepository) -> None:
        self.ticket_category_repository = ticket_category_repository

    async def get_ticket_category_by_id(self, category_id: int) -> TicketCategory | None:
        return await self.ticket_category_repository.get_ticket_category_by_id(category_id)

    async def create_ticket_category(self, data: TicketCategoryCreateSchema) -> TicketCategory:
        category = TicketCategory(**data.model_dump())
        return await self.ticket_category_repository.create_ticket_category(category)

    async def get_ticket_categories(self) -> Sequence[TicketCategory]:
        return await self.ticket_category_repository.get_all_ticket_categories()

    async def update_ticket_category(
        self,
        ticket_category: TicketCategory,
        data: TicketCategoryUpdateSchema,
    ) -> TicketCategory:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(ticket_category, field, value)
        return await self.ticket_category_repository.update_ticket_category(ticket_category)

    async def delete_ticket_category(self, ticket_category: TicketCategory) -> None:
        await self.ticket_category_repository.delete_ticket_category(ticket_category)
