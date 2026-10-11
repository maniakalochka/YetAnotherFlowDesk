import enum
import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flowdesk.infrastructure.database.base import Base
from flowdesk.modules.tickets.models import Ticket, TicketComment, TicketStatusHistory


class UserRole(enum.StrEnum):
    ADMIN = "admin"
    SUPPORT = "support"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    fname: Mapped[str] = mapped_column(nullable=False)
    lname: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(nullable=False, default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="author",
        foreign_keys="Ticket.author_id",
    )
    assigned_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="assignee",
        foreign_keys="Ticket.assignee_id",
    )
    ticket_status_changes: Mapped[list["TicketStatusHistory"]] = relationship(
        "TicketStatusHistory",
        back_populates="changed_by",
    )
    ticket_comments: Mapped[list["TicketComment"]] = relationship(
        "TicketComment",
        back_populates="author",
    )
