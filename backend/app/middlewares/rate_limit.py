"""Rate limiting middleware — in-memory sliding window per IP.

Phase 6 implementation: a lightweight in-memory rate limiter for sensitive
endpoints (login, refresh, password-reset). For production with multiple
workers or instances, replace the InMemoryStore with a Redis-backed store
(documented in docs/architecture.md).

The limiter is applied as a FastAPI dependency on specific routes, not as a
global middleware, so it only affects the configured endpoints.
"""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field

from fastapi import Request

from app.core.exceptions import RateLimitError


@dataclass
class _Window:
    hits: list[float] = field(default_factory=list)


class InMemoryRateLimiter:
    """Sliding window rate limiter. Thread-safe enough for async single-process.

    For multi-worker uvicorn, each worker has its own counter — the effective
    limit is multiplied by the number of workers. This is acceptable for the
    boilerplate; use Redis for precise distributed limiting.
    """

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._buckets: dict[str, _Window] = defaultdict(_Window)

    def check(self, key: str) -> None:
        """Raise RateLimitError if key has exceeded the limit. Otherwise record."""
        now = time.monotonic()
        cutoff = now - self._window
        w = self._buckets[key]
        # Prune old hits
        w.hits = [t for t in w.hits if t > cutoff]
        if len(w.hits) >= self._max:
            raise RateLimitError(
                "Demasiados intentos. Espere antes de intentar nuevamente.",
                code="rate_limited",
            )
        w.hits.append(now)


# Pre-configured limiters for sensitive endpoints.
_login_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)
_refresh_limiter = InMemoryRateLimiter(max_requests=30, window_seconds=60)
_reset_limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60)


def rate_limit_login(request: Request) -> None:
    """Dependency: rate-limit login attempts per IP (10/min)."""
    ip = request.client.host if request.client else "unknown"
    _login_limiter.check(f"login:{ip}")


def rate_limit_refresh(request: Request) -> None:
    """Dependency: rate-limit refresh attempts per IP (30/min)."""
    ip = request.client.host if request.client else "unknown"
    _refresh_limiter.check(f"refresh:{ip}")


def rate_limit_reset(request: Request) -> None:
    """Dependency: rate-limit password reset per IP (5/min)."""
    ip = request.client.host if request.client else "unknown"
    _reset_limiter.check(f"reset:{ip}")