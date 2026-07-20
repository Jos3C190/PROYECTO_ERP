"""Structured logging via structlog.

We render human-readable lines in development and JSON lines in production/test
so logs can be ingested by Loki/ELK/Datadog without extra parsing.

CRITICAL for security (OWASP A09): never log passwords, full tokens, PII in
clear text. Use `secret()` helper to mask values, and keep request loggers at
INFO for security events and DEBUG for routine flow.
"""
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from app.core.config import settings


def _should_use_json() -> bool:
    return settings.ENVIRONMENT in {"production", "staging", "test"}


def configure_logging() -> None:
    """Configure stdlib logging + structlog processors. Idempotent."""
    level = getattr(logging, settings.LOG_LEVEL, logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
        force=True,
    )

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if _should_use_json():
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Quiet noisy libraries in dev too.
    for noisy in ("uvicorn.access", "uvicorn.error", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING if not settings.DEBUG else logging.INFO)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


def secret(value: str | None, visible: int = 0) -> str:
    """Mask a secret for safe logging. `visible` chars kept at the start."""
    if not value:
        return "<empty>"
    if visible and len(value) > visible:
        return value[:visible] + "***"
    return "***"