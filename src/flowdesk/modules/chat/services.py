import uuid

from flowdesk.modules.chat.models import TicketChatMessage
from flowdesk.modules.chat.repositories import TicketChatRepository
from flowdesk.modules.chat.schemas import TicketChatMessageCreateSchema


class TicketChatService:
    def __init__(self, repository: TicketChatRepository) -> None:
        self.repository = repository

    async def create_message(
        self,
        data: TicketChatMessageCreateSchema,
        ticket_id: uuid.UUID,
        author_id: uuid.UUID,
    ) -> TicketChatMessage:
        message = TicketChatMessage(
            text=data.content,
            ticket_id=ticket_id,
            author_id=author_id,
        )
        return await self.repository.create_ticket_chat_message(message)

    async def get_message_history(self, ticket_id: uuid.UUID) -> list[TicketChatMessage]:
        return await self.repository.get_ticket_chat_messages_by_ticket_id(ticket_id)
