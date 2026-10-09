from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from flowdesk.core import settings

engine = create_async_engine(
    settings.DB_URL,
    isolation_level="READ COMMITTED",
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
