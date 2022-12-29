from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from loguru import logger

from ..core.settings import Settings


async def connect_to_db(app: FastAPI,settings: Settings) -> None:
    """
    Creates and assings database engine to an application
    """

    logger.info("Connecting to db")

    engine = create_async_engine(settings.async_db_conn_str)
    app.state.engine = engine

    logger.info("Connected to db")


async def disconnect_from_db(app: FastAPI) -> None:
    """
    Disposes an application's database engine
    """

    logger.info("Disconnecting from db")

    await app.state.engine.dispose()

    logger.info("Connection has been closed")
