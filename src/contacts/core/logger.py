import sys
import logging

import loguru

from .settings import Settings


def configure_logging(settings: Settings) -> None:
    if settings.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    handler = {
        "sink": sys.stderr,
        "level": log_level,
    }
    loguru.logger.configure(handlers=[handler])
