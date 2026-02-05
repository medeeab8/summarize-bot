from fastapi import FastAPI
from .api.v1.routes.router import router

def create_app() -> FastAPI:
    app = FastAPI(title="Summarize Bot API", version="1.0.0")

    app.include_router(router, prefix="/api/v1")

    return app

app = create_app()