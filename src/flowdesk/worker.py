from faststream import AckPolicy, FastStream

from flowdesk.infrastructure.broker import queues
from flowdesk.infrastructure.broker.rabbit import broker
from flowdesk.infrastructure.database.session import AsyncSessionLocal
from flowdesk.modules.notifications.model import Notification
from flowdesk.modules.notifications.repository import NotificationRepository
from flowdesk.modules.notifications.schemas.messages import CreateNotificationMessage
from flowdesk.modules.notifications.service import NotificationService

faststream = FastStream(broker)


@broker.subscriber(
    queues.notification,
    ack_policy=AckPolicy.NACK_ON_ERROR,
)
async def create_notification(
    message: CreateNotificationMessage,
) -> None:
    async with AsyncSessionLocal() as session:
        repository = NotificationRepository(session)
        service = NotificationService(repository)

        notification = Notification(
            event_id=message.event_id,
            user_id=message.user_id,
            ticket_id=message.ticket_id,
            type=message.type,
            title=message.title,
            message=message.message,
        )

        await service.add(notification)
