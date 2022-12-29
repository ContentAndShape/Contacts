from typing import Callable

from fastapi import FastAPI
from loguru import logger

from .settings import Settings
from contacts.db.events import connect_to_db, disconnect_from_db


def get_startup_handler(app: FastAPI, settings: Settings) -> Callable:
    async def start_app() -> None:
        logger.debug("Starting app")

        await connect_to_db(app, settings)

    return start_app


def get_shutdown_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        logger.debug("Stopping app")
        
        await disconnect_from_db(app)

    return stop_app
