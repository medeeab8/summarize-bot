from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.routes.router import router
from .core.logging import LoggingSettings, configure_logging
from .exceptions.handlers import register_exception_handlers
from .core.settings import get_settings

logging_settings = LoggingSettings(level="DEBUG")  # Set log level to INFO for production
configure_logging(logging_settings)  # Set log level to DEBUG for development
settings = get_settings()

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "null",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(router, prefix=settings.API_PREFIX)

    return app

app = create_app()