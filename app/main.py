from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.routes import router
from app.db import close_pool


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    close_pool()


app = FastAPI(
    title="Sealos FastAPI PostgreSQL Example",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)
