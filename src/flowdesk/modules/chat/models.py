import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flowdesk.infrastructure.database.base import Base

if TYPE_CHECKING:
    from flowdesk.modules.tickets.models import Ticket
    from flowdesk.modules.users.models import User


class TicketChatMessage(Base):
    __tablename__ = "ticket_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(nullable=False)
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False
    )
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="messages")
    author: Mapped["User"] = relationship("User", back_populates="ticket_comments")
