import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import select

from flowdesk.infrastructure.broker import queues
from flowdesk.infrastructure.broker.rabbit import broker
from flowdesk.infrastructure.database.session import AsyncSessionLocal
from flowdesk.infrastructure.outbox.models import OutboxEvent
from flowdesk.infrastructure.outbox.publisher import OutboxPublisher

logger = logging.getLogger(__name__)


async def process_outbox(publisher: OutboxPublisher) -> None:
    async with AsyncSessionLocal() as session:
        stmt = (
            select(OutboxEvent.id)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at)
            .limit(50)
        )
        event_ids = (await session.scalars(stmt)).all()

        for event_id in event_ids:
            async with AsyncSessionLocal() as session:
                event = await session.get(OutboxEvent, event_id)

                if event is None:
                    continue

                if event.published_at is not None:
                    continue

                try:
                    await publisher.publish(event)

                    event.published_at = datetime.now(UTC)
                    await session.commit()

                except Exception:
                    await session.rollback()
                    logger.exception(
                        "Failed to publish event %s",
                        event_id,
                    )


async def main() -> None:
    publisher = OutboxPublisher(broker)

    async with broker:
        await broker.declare_queue(queues.notification)

        while True:
            try:
                await process_outbox(publisher)
            except Exception:
                logger.exception("Outbox processing failed")

            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
