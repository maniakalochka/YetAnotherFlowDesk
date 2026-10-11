import uuid
from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.modules.tickets.models import (
    Ticket,
    TicketCategory,
    TicketComment,
    TicketStatusHistory,
)
from flowdesk.modules.tickets.schemas import TicketUpdateSchema


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_ticket_by_id(self, ticket_id: uuid.UUID) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_ticket(self, ticket: Ticket, author_id: uuid.UUID) -> Ticket:
        ticket.author_id = author_id
        self.session.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

    async def update_ticket(
        self, ticket_id: uuid.UUID, ticket_data: TicketUpdateSchema
    ) -> Ticket | None:
        stmt = (
            update(Ticket)
            .where(Ticket.id == ticket_id)
            .values(
                title=ticket_data.title,
                description=ticket_data.description,
                status=ticket_data.status,
                priority=ticket_data.priority,
                assignee_id=ticket_data.assignee_id,
                ticket_category_id=ticket_data.ticket_category_id,
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        updated_ticket = await self.get_ticket_by_id(ticket_id)
        return updated_ticket

    async def delete_ticket(self, ticket: Ticket) -> None:
        stmt = update(Ticket).where(Ticket.id == ticket.id).values(archived=True)
        await self.session.execute(stmt)
        await self.session.commit()


class TicketStatusHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_ticket_status_history(
        self, ticket_status_history: TicketStatusHistory
    ) -> None:
        self.session.add(ticket_status_history)
        await self.session.commit()

    async def get_ticket_status_history_by_ticket_id(
        self, ticket_id: uuid.UUID
    ) -> Sequence[TicketStatusHistory]:
        stmt = select(TicketStatusHistory).where(TicketStatusHistory.ticket_id == ticket_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_ticket_status_history(
        self, ticket_status_history: TicketStatusHistory
    ) -> TicketStatusHistory:
        stmt = (
            update(TicketStatusHistory)
            .where(TicketStatusHistory.id == ticket_status_history.id)
            .values(
                ticket_id=ticket_status_history.ticket_id,
                old_status=ticket_status_history.old_status,
                new_status=ticket_status_history.new_status,
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.refresh(ticket_status_history)
        return ticket_status_history


class TicketCommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_ticket_comment(self, ticket_comment: TicketComment) -> None:
        self.session.add(ticket_comment)
        await self.session.commit()

    async def get_ticket_comments_by_ticket_id(
        self, ticket_id: uuid.UUID
    ) -> Sequence[TicketComment]:
        stmt = select(TicketComment).where(TicketComment.ticket_id == ticket_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_ticket_comment(self, ticket_comment: TicketComment) -> TicketComment:
        stmt = (
            update(TicketComment)
            .where(TicketComment.id == ticket_comment.id)
            .values(
                text=ticket_comment.text,
                ticket_id=ticket_comment.ticket_id,
                author_id=ticket_comment.author_id,
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.refresh(ticket_comment)
        return ticket_comment


class TicketCategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_ticket_category_by_id(self, category_id: int) -> TicketCategory | None:
        stmt = select(TicketCategory).where(TicketCategory.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_ticket_categories(self) -> Sequence[TicketCategory]:
        stmt = select(TicketCategory)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_ticket_category(self, ticket_category: TicketCategory) -> TicketCategory:
        self.session.add(ticket_category)
        await self.session.commit()
        await self.session.refresh(ticket_category)
        return ticket_category

    async def update_ticket_category(self, ticket_category: TicketCategory) -> TicketCategory:
        stmt = (
            update(TicketCategory)
            .where(TicketCategory.id == ticket_category.id)
            .values(
                name=ticket_category.name,
                description=ticket_category.description,
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.refresh(ticket_category)
        return ticket_category
