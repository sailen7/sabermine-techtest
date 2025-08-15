from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from src.database import engine
from src.tasks import router as tasks_router


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Create the database and tables on startup
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(tasks_router)
