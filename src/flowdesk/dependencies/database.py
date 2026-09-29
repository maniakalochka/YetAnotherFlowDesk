from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.core.logging import get_logger
from flowdesk.infrastructure.database.session import AsyncSessionLocal

logger = get_logger(__name__)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            logger.exception("Error occurred during database session.")
            await session.rollback()
            raise
