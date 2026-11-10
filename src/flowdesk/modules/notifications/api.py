import uuid

from fastapi import APIRouter, HTTPException

from flowdesk.dependencies.notification import NotificationServiceDep
from flowdesk.dependencies.user import CurrentUserDep
from flowdesk.modules.notifications.model import Notification
from flowdesk.modules.notifications.schemas.notification import (
    NotificationCreateSchema,
    NotificationSchema,
    NotificationUpdateSchema,
)

notification_router = APIRouter(tags=["Notifications"])


@notification_router.get("/notifications", response_model=list[NotificationSchema])
async def get_notifications(
    notification_service: NotificationServiceDep,
    current_user: CurrentUserDep,
) -> list[NotificationSchema] | None:
    notifications = await notification_service.get_notifications_by_user_id(current_user.id)
    if notifications is None:
        return []
    return [NotificationSchema.model_validate(notification) for notification in notifications]


@notification_router.patch(
    "/notifications/{notification_id}/read", response_model=NotificationUpdateSchema
)
async def mark_notification_as_read(
    notification_id: uuid.UUID,
    notification_service: NotificationServiceDep,
    current_user: CurrentUserDep,
) -> NotificationUpdateSchema:
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    await notification_service.mark_notification_as_read(notification_id)
    return NotificationUpdateSchema(is_read=True)


@notification_router.post(
    "/notifications", response_model=NotificationCreateSchema, status_code=201
)
async def create_notification(
    notification: Notification,
    notification_service: NotificationServiceDep,
) -> NotificationCreateSchema:
    created_notification = await notification_service.add(notification)
    return NotificationCreateSchema.model_validate(created_notification)
