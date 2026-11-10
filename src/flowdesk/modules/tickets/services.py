import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.infrastructure.outbox.models import OutboxEvent
from flowdesk.infrastructure.outbox.repository import OutBoxRepository
from flowdesk.modules.notifications.model import NotificationType
from flowdesk.modules.notifications.schemas.messages import CreateNotificationMessage
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
    def __init__(
        self,
        ticket_repository: TicketRepository,
        outbox_repository: OutBoxRepository,
        session: AsyncSession,
    ):
        self.ticket_repository = ticket_repository
        self.outbox_repository = outbox_repository
        self.session = session

    async def get_ticket_by_id(self, ticket_id: uuid.UUID) -> Ticket | None:
        return await self.ticket_repository.get_ticket_by_id(ticket_id)

    async def create_ticket(self, data: TicketCreateSchema, author_id: uuid.UUID) -> Ticket:
        try:
            ticket = Ticket(**data.model_dump(), author_id=author_id)
            ticket = await self.ticket_repository.create_ticket(ticket, author_id)

            notification_message = CreateNotificationMessage(
                event_id=uuid.uuid4(),
                user_id=author_id,
                ticket_id=ticket.id,
                type=NotificationType.TICKET_CREATED,
                title=f"New Ticket Created: {ticket.title}",
                message=f"A new ticket has been created with ID: {ticket.id}",
            )
            outbox_event = OutboxEvent(
                id=notification_message.event_id,
                event_type="ticket.created",
                payload=notification_message.model_dump(mode="json"),
            )
            await self.outbox_repository.create_outbox_event(outbox_event)
            await self.session.commit()
            return ticket
        except Exception as e:
            await self.session.rollback()
            raise e
        return ticket

    async def update_ticket(
        self, ticket_id: uuid.UUID, ticket_data: TicketUpdateSchema
    ) -> Ticket | None:
        return await self.ticket_repository.update_ticket(ticket_id, ticket_data)

    async def delete_ticket(self, ticket: Ticket) -> None:
        await self.ticket_repository.delete_ticket(ticket)

    async def list_tickets(self, skip: int = 0, limit: int = 100) -> Sequence[Ticket]:
        return await self.ticket_repository.list_tickets(skip=skip, limit=limit)

    async def list_tickets_by_author_id(
        self, author_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[Ticket]:
        return await self.ticket_repository.list_tickets_by_author_id(
            author_id, skip=skip, limit=limit
        )


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
