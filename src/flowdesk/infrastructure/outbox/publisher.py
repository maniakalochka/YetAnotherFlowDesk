from faststream.rabbit import RabbitBroker
from pamqp.commands import Basic

from flowdesk.infrastructure.broker.queues import notification
from flowdesk.infrastructure.outbox.models import OutboxEvent
from flowdesk.modules.notifications.schemas.messages import CreateNotificationMessage


class OutboxPublisher:
    def __init__(self, broker: RabbitBroker):
        self.broker = broker

    async def publish(self, event: OutboxEvent) -> None:
        if event.event_type != "ticket.created":
            raise ValueError(f"Unsupported event type: {event.event_type}")

        message = CreateNotificationMessage.model_validate(event.payload)

        confirmation = await self.broker.publish(
            message=message,
            queue=notification,
            persist=True,
            mandatory=True,
            message_id=str(event.id),
            timeout=10,
        )

        if not isinstance(confirmation, Basic.Ack):
            raise RuntimeError(f"RabbitMQ did not confirm event {event.id}")
