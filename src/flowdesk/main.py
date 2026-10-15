from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.core.logging import get_logger
from flowdesk.dependencies.database import get_async_session
from flowdesk.infrastructure.database.session import (
    AsyncSessionLocal,
    engine,
)
from flowdesk.modules.chat.api import chat_router
from flowdesk.modules.tickets.api import tickets_router
from flowdesk.modules.users.api import user_router

logger = get_logger("flowdesk.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger.info("Application startup")

    app.state.engine = engine
    app.state.session_factory = AsyncSessionLocal

    try:
        logger.info("Application started successfully")
        yield
    finally:
        await engine.dispose()
        logger.info("Application shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(
    user_router,
    tags=["users"],
)

app.include_router(chat_router, tags=["chat"])
app.include_router(tickets_router, tags=["tickets"])


@app.get("/ready")
async def readiness(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "flowdesk.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
