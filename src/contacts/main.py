from fastapi import FastAPI

from core.settings import get_settings
from core.logger import configure_logging
from core.events import get_startup_handler, get_shutdown_handler
from api.main_router import router


def get_app() -> FastAPI:
    settings = get_settings()

    configure_logging(settings)

    app = FastAPI()
    app.state.secret = settings.secret
    app.add_event_handler(
        "startup", 
        get_startup_handler(app, settings),
    )
    app.add_event_handler(
        "shutdown", 
        get_shutdown_handler(app),
    )
    app.include_router(router,prefix=settings.api_prefix)

    return app


app = get_app()
