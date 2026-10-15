import uuid
from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.modules.tickets.exceptions import (
    TicketCategoryAlreadyExistsError,
    TicketCategoryInUseError,
)
from flowdesk.modules.tickets.models import (
    Ticket,
    TicketCategory,
    TicketStatusHistory,
)
from flowdesk.modules.tickets.schemas import TicketUpdateSchema


class TicketBaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


class TicketRepository(TicketBaseRepository):
    async def get_ticket_by_id(self, ticket_id: uuid.UUID) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_tickets(self, skip: int = 0, limit: int = 100) -> Sequence[Ticket]:
        stmt = select(Ticket).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_ticket(self, ticket: Ticket, author_id: uuid.UUID) -> Ticket:
        ticket.author_id = author_id
        self.session.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

    async def update_ticket(
        self, ticket_id: uuid.UUID, ticket_data: TicketUpdateSchema
    ) -> Ticket | None:
        values = ticket_data.model_dump(exclude_unset=True)
        if not values:
            return await self.get_ticket_by_id(ticket_id)

        stmt = (
            update(Ticket)
            .where(Ticket.id == ticket_id)
            .values(**values)
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
        await self.session.refresh(ticket)


class TicketStatusHistoryRepository(TicketBaseRepository):
    async def create_ticket_status_history(
        self, ticket_status_history: TicketStatusHistory
    ) -> TicketStatusHistory:
        self.session.add(ticket_status_history)
        await self.session.commit()
        await self.session.refresh(ticket_status_history)
        return ticket_status_history

    async def get_ticket_status_history_by_ticket_id(
        self, ticket_id: uuid.UUID
    ) -> Sequence[TicketStatusHistory]:
        stmt = (
            select(TicketStatusHistory)
            .where(TicketStatusHistory.ticket_id == ticket_id)
            .order_by(
                TicketStatusHistory.created_at,
                TicketStatusHistory.id,
            )
        )
        result = await self.session.scalars(stmt)
        return list(result.all())


class TicketCategoryRepository(TicketBaseRepository):
    async def get_ticket_category_by_id(self, category_id: int) -> TicketCategory | None:
        stmt = select(TicketCategory).where(TicketCategory.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_ticket_categories(self) -> Sequence[TicketCategory]:
        stmt = select(TicketCategory).order_by(TicketCategory.name, TicketCategory.id)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def create_ticket_category(self, ticket_category: TicketCategory) -> TicketCategory:
        self.session.add(ticket_category)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise TicketCategoryAlreadyExistsError from None
        await self.session.refresh(ticket_category)
        return ticket_category

    async def update_ticket_category(self, ticket_category: TicketCategory) -> TicketCategory:
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise TicketCategoryAlreadyExistsError from None
        await self.session.refresh(ticket_category)
        return ticket_category

    async def delete_ticket_category(self, ticket_category: TicketCategory) -> None:
        await self.session.delete(ticket_category)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise TicketCategoryInUseError from None
