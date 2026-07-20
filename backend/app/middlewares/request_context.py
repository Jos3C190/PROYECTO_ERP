"""Request context middleware: assigns a request ID and binds it to structlog
contextvars for the lifetime of the request. Also emits a structured access log
line at the end of each HTTP request.

Security note (A09): we log method, path, status, duration, request_id, and the
client IP. We DO NOT log request bodies, headers, or query strings that may
contain secrets or PII.
"""
from __future__ import annotations

import time
import uuid

import structlog
from starlette.types import ASGIApp, Receive, Scope, Send

log = structlog.get_logger("app.access")


def _client_ip(scope: Scope) -> str:
    client = scope.get("client")
    return client[0] if client else "-"


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=scope.get("method", ""),
            path=scope.get("path", ""),
        )

        start = time.perf_counter()
        status_code: int = 500

        async def send_with_log(message: object) -> None:
            assert isinstance(message, dict)
            nonlocal status_code
            if message.get("type") == "http.response.start":
                status_code = int(message.get("status", 500))
            await send(message)

        try:
            await self.app(scope, receive, send_with_log)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000.0
            log.info(
                "http_request",
                status=status_code,
                duration_ms=round(duration_ms, 2),
                ip=_client_ip(scope),
            )
            structlog.contextvars.clear_contextvars()