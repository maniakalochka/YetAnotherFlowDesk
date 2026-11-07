import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from flowdesk.modules.notifications.model import NotificationType


class NotificationSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: uuid.UUID = Field(..., description="Notification ID")
    user_id: uuid.UUID = Field(..., description="User ID associated with the notification")
    type: NotificationType = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    is_read: bool = Field(..., description="Notification read status")
    created_at: datetime.datetime = Field(..., description="Notification creation timestamp")


class NotificationCreateSchema(NotificationSchema):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    user_id: uuid.UUID = Field(..., description="User ID associated with the notification")
    type: NotificationType = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")


class NotificationUpdateSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    is_read: bool = Field(..., description="Notification read status")
