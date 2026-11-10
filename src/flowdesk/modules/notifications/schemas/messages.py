import uuid

from pydantic import BaseModel, ConfigDict

from flowdesk.modules.notifications.model import NotificationType


class CreateNotificationMessage(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    event_id: uuid.UUID
    user_id: uuid.UUID
    ticket_id: uuid.UUID
    type: NotificationType
    title: str
    message: str
