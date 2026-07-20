"""Map application exceptions to HTTP responses.

Client messages are generic; details go to logs only (OWASP A05).
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.core.logging import get_logger

log = get_logger(__name__)


def _payload(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message})


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    log.warning(
        "app_error",
        code=exc.code,
        message=exc.message,
        path=request.url.path,
        method=request.method,
    )
    return _payload(exc.code, exc.message, exc.status_code)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log.exception("unhandled_exception", path=request.url.path, method=request.method)
    return _payload("internal_error", "Error interno del servidor.", 500)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)