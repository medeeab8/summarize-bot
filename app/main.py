from fastapi import FastAPI
from .api.v1.routes.router import router
from .core.logging import LoggingSettings, configure_logging
from .exceptions.handlers import register_exception_handlers

logging_settings = LoggingSettings(level="DEBUG")  # Set log level to INFO for production
configure_logging(logging_settings)  # Set log level to DEBUG for development

def create_app() -> FastAPI:
    app = FastAPI(title="Summarize Bot API", version="1.0.0")

    register_exception_handlers(app)
    app.include_router(router, prefix="/api/v1")

    return app

app = create_app()