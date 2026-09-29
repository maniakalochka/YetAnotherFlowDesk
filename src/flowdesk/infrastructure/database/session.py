from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from flowdesk.core import settings

engine = create_async_engine(
    settings.DB_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
