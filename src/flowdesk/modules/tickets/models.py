import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flowdesk.infrastructure.database.base import Base

if TYPE_CHECKING:
    from flowdesk.modules.users.models import User


class TicketStatus(enum.StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class TicketPriority(enum.StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[TicketStatus] = mapped_column(nullable=False, default=TicketStatus.OPEN)
    priority: Mapped[TicketPriority] = mapped_column(nullable=False, default=TicketPriority.LOW)
    archived: Mapped[bool] = mapped_column(nullable=False, default=False)

    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    assignee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    ticket_category_id: Mapped[int] = mapped_column(
        ForeignKey("ticket_categories.id"), nullable=False
    )

    author: Mapped["User"] = relationship(
        "User", foreign_keys=[author_id], back_populates="created_tickets"
    )
    assignee: Mapped["User | None"] = relationship(
        "User", foreign_keys=[assignee_id], back_populates="assigned_tickets"
    )

    ticket_category: Mapped["TicketCategory | None"] = relationship(
        "TicketCategory", back_populates="tickets"
    )
    comments: Mapped[list["TicketComment"]] = relationship(
        "TicketComment",
        back_populates="ticket",
    )
    history: Mapped[list["TicketStatusHistory"]] = relationship(
        "TicketStatusHistory",
        back_populates="ticket",
    )


class TicketStatusHistory(Base):
    __tablename__ = "ticket_status_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False
    )
    old_status: Mapped[TicketStatus | None] = mapped_column(nullable=True, default=None)
    new_status: Mapped[TicketStatus] = mapped_column(nullable=False)

    changed_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="history")
    changed_by: Mapped["User"] = relationship("User", back_populates="ticket_status_changes")


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(nullable=False)
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False
    )
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="comments")
    author: Mapped["User"] = relationship("User", back_populates="ticket_comments")


class TicketCategory(Base):
    __tablename__ = "ticket_categories"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str] = mapped_column(nullable=True)

    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="ticket_category",
    )
