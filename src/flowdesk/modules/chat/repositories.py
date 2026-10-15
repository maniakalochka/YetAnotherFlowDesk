import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.modules.chat.models import TicketChatMessage


class TicketChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_ticket_chat_messages_by_ticket_id(
        self, ticket_id: uuid.UUID
    ) -> list[TicketChatMessage]:
        stmt = (
            select(TicketChatMessage)
            .where(TicketChatMessage.ticket_id == ticket_id)
            .order_by(TicketChatMessage.created_at, TicketChatMessage.id)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def create_ticket_chat_message(
        self, ticket_chat_message: TicketChatMessage
    ) -> TicketChatMessage:
        self.session.add(ticket_chat_message)
        await self.session.commit()
        await self.session.refresh(ticket_chat_message)
        return ticket_chat_message

    async def update_ticket_chat_message(
        self, ticket_chat_message: TicketChatMessage
    ) -> TicketChatMessage:
        stmt = (
            update(TicketChatMessage)
            .where(TicketChatMessage.id == ticket_chat_message.id)
            .values(
                text=ticket_chat_message.text,
                ticket_id=ticket_chat_message.ticket_id,
                author_id=ticket_chat_message.author_id,
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.refresh(ticket_chat_message)
        return ticket_chat_message
