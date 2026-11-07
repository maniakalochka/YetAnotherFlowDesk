import uuid

from flowdesk.modules.notifications.model import Notification
from flowdesk.modules.notifications.repository import NotificationRepository


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def add(self, notification: Notification) -> Notification:
        return await self.repository.add_notification(notification)

    async def get_notifications_by_user_id(self, user_id: uuid.UUID) -> list[Notification] | None:
        return await self.repository.get_notifications_by_user_id(user_id)

    async def mark_notification_as_read(self, notification_id: uuid.UUID) -> None:
        await self.repository.mark_notification_as_read(notification_id)
