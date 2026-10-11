import datetime
import uuid

from pydantic import BaseModel, Field

from flowdesk.modules.tickets.models import TicketPriority, TicketStatus


class TicketSchema(BaseModel):
    id: uuid.UUID = Field(..., description="The unique identifier of the ticket")
    title: str = Field(..., description="The title of the ticket")
    description: str = Field(..., description="The detailed description of the ticket")
    status: TicketStatus = Field(..., description="The current status of the ticket")
    priority: TicketPriority = Field(..., description="The priority level of the ticket")
    created_at: datetime.datetime = Field(
        ..., description="The timestamp when the ticket was created"
    )
    updated_at: datetime.datetime = Field(
        ..., description="The timestamp when the ticket was last updated"
    )


class TicketCreateSchema(BaseModel):
    title: str = Field(..., description="The title of the ticket")
    description: str = Field(..., description="The detailed description of the ticket")
    status: TicketStatus = Field(..., description="The current status of the ticket")
    priority: TicketPriority = Field(..., description="The priority level of the ticket")


class TicketUpdateSchema(BaseModel):
    title: str | None = Field(None, description="The title of the ticket")
    description: str | None = Field(None, description="The detailed description of the ticket")
    status: TicketStatus | None = Field(None, description="The current status of the ticket")
    priority: TicketPriority | None = Field(None, description="The priority level of the ticket")
    assignee_id: uuid.UUID | None = Field(
        None, description="The unique identifier of the user assigned to the ticket"
    )
    ticket_category_id: int | None = Field(
        None, description="The unique identifier of the ticket category"
    )
