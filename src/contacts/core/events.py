from typing import Callable

from fastapi import FastAPI
from loguru import logger

from .settings import Settings, get_settings
from .logger import configure_logging


def get_startup_handler(app: FastAPI, settings: Settings) -> Callable:
    async def start_app() -> None:
        configure_logging(settings=get_settings())
        logger.debug("Starting app")
        ...

    return start_app


def get_stop_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        logger.debug("Stopping app")
        ...

    return stop_app
