from fastapi import FastAPI
from .api.v1.routes.router import router
from .core.logging import LoggingSettings, configure_logging

logging_settings = LoggingSettings(level="DEBUG")
configure_logging(logging_settings)  # Set log level to DEBUG for development

def create_app() -> FastAPI:
    app = FastAPI(title="Summarize Bot API", version="1.0.0")

    app.include_router(router, prefix="/api/v1")

    return app

app = create_app()