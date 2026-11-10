from faststream.rabbit import Channel, RabbitBroker

from flowdesk.core.config import settings

broker = RabbitBroker(
    url=settings.RABBITMQ_URL,
    default_channel=Channel(
        publisher_confirms=True,
        on_return_raises=True,
    ),
)
