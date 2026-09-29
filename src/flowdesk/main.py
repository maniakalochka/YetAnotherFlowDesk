from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from flowdesk.core.logging import get_logger
from flowdesk.infrastructure.database.session import AsyncSessionLocal, engine
from flowdesk.modules.users.api import user_router

app = FastAPI()

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


app.include_router(
    user_router,
    tags=["users"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
