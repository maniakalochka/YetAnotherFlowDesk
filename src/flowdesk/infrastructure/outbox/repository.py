from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.infrastructure.outbox.models import OutboxEvent


class OutBoxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_outbox_event(self, event: OutboxEvent) -> OutboxEvent:
        self.session.add(event)
        await self.session.flush()
        return event
