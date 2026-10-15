import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TicketChatMessageCreateSchema(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Content of the chat message",
    )

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message content must not be blank")
        return value


class TicketChatMessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique identifier for the chat message")
    ticket_id: uuid.UUID = Field(
        ..., description="Identifier of the ticket associated with the chat message"
    )
    author_id: uuid.UUID = Field(
        ..., description="Identifier of the user who authored the chat message"
    )
    content: str = Field(
        ...,
        validation_alias="text",
        description="Content of the chat message",
    )
    created_at: datetime.datetime
