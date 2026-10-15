import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from flowdesk.modules.tickets.models import TicketPriority, TicketStatus


class TicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    ticket_category_id: int = Field(..., gt=0, description="The ticket category identifier")


class TicketUpdateSchema(BaseModel):
    title: str | None = Field(None, description="The title of the ticket")
    description: str | None = Field(None, description="The detailed description of the ticket")
    priority: TicketPriority | None = Field(None, description="The priority level of the ticket")
    assignee_id: uuid.UUID | None = Field(
        None, description="The unique identifier of the user assigned to the ticket"
    )
    ticket_category_id: int | None = Field(
        None, description="The unique identifier of the ticket category"
    )


class TicketCategoryCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)


class TicketCategoryUpdateSchema(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "TicketCategoryUpdateSchema":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class TicketCategorySchema(TicketCategoryCreateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class TicketStatusUpdateSchema(BaseModel):
    status: TicketStatus


class TicketStatusHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ticket_id: uuid.UUID
    old_status: TicketStatus | None
    new_status: TicketStatus
    changed_by_id: uuid.UUID
    created_at: datetime.datetime
