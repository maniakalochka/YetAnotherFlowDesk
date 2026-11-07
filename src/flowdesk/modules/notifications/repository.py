import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.modules.notifications.model import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_notification(self, notification: Notification) -> Notification:
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def get_notifications_by_user_id(self, user_id: uuid.UUID) -> list[Notification] | None:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        result = await self.session.scalars(stmt)
        if not result:
            return None
        return list(result.all())

    async def mark_notification_as_read(self, notification_id: uuid.UUID) -> None:
        notification = await self.session.get(Notification, notification_id)
        if not notification:
            raise ValueError("Notification not found")
        notification.is_read = True
        await self.session.commit()
