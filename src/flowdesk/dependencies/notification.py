from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.dependencies.database import get_async_session
from flowdesk.modules.notifications.repository import NotificationRepository
from flowdesk.modules.notifications.service import NotificationService


def get_notification_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> NotificationRepository:
    return NotificationRepository(session)


def get_notification_service(
    repository: Annotated[NotificationRepository, Depends(get_notification_repository)],
) -> NotificationService:
    return NotificationService(repository)


NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]
