from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    # Register all exception handlers on the app instance.
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        # Handle standard HTTP errors raised by FastAPI.
        logger.warning("HTTP error", extra={"path": request.url.path, "detail": exc.detail})
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Handle request validation errors (422).
        logger.warning("Validation error", extra={"path": request.url.path})
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Catch-all for unexpected errors.
        print(logger)
        logger.exception("Unhandled error", extra={"path": request.url.path})
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
