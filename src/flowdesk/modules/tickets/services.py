import uuid
from collections.abc import Sequence
from typing import Any

from flowdesk.modules.tickets.models import (
    Ticket,
    TicketCategory,
    TicketComment,
    TicketStatusHistory,
)
from flowdesk.modules.tickets.repositories import (
    TicketCategoryRepository,
    TicketCommentRepository,
    TicketRepository,
    TicketStatusHistoryRepository,
)
from flowdesk.modules.tickets.schemas import TicketCreateSchema, TicketUpdateSchema


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


class TicketStatusHistoryService:
    def __init__(self, ticket_status_history_repository: TicketStatusHistoryRepository) -> None:
        self.ticket_status_history_repository = ticket_status_history_repository

    async def create_ticket_status_history(
        self, ticket_status_history: TicketStatusHistory
    ) -> None:
        await self.ticket_status_history_repository.create_ticket_status_history(
            ticket_status_history
        )

    async def get_ticket_status_history_by_ticket_id(
        self, ticket_id: uuid.UUID
    ) -> Sequence[Any] | None:
        return await self.ticket_status_history_repository.get_ticket_status_history_by_ticket_id(
            ticket_id
        )

    async def update_ticket_status_history(
        self, ticket_status_history: TicketStatusHistory
    ) -> None:
        await self.ticket_status_history_repository.update_ticket_status_history(
            ticket_status_history
        )


class TicketCommentService:
    def __init__(self, ticket_comment_repository: TicketCommentRepository) -> None:
        self.ticket_comment_repository = ticket_comment_repository

    async def create_ticket_comment(self, ticket_comment: TicketComment) -> None:
        await self.ticket_comment_repository.create_ticket_comment(ticket_comment)

    async def get_ticket_comments_by_ticket_id(self, ticket_id: uuid.UUID) -> Sequence[Any] | None:
        return await self.ticket_comment_repository.get_ticket_comments_by_ticket_id(ticket_id)

    async def update_ticket_comment(self, ticket_comment: TicketComment) -> None:
        await self.ticket_comment_repository.update_ticket_comment(ticket_comment)


class TicketCategoryService:
    def __init__(self, ticket_category_repository: TicketCategoryRepository):
        self.ticket_category_repository = ticket_category_repository

    async def create_ticket_category(self, ticket_category: TicketCategory) -> None:
        await self.ticket_category_repository.create_ticket_category(ticket_category)

    async def get_ticket_categories(self) -> Sequence[TicketCategory]:
        return await self.ticket_category_repository.get_all_ticket_categories()

    async def update_ticket_category(self, ticket_category: TicketCategory) -> None:
        await self.ticket_category_repository.update_ticket_category(ticket_category)
