"""Shared pytest fixtures.

We deliberately avoid a global DB fixture for unit tests. Integration tests opt
in with the `integration` marker and use the `db_session` fixture, which spins
up a unique schema-per-test via a sync Postgres connection.

Phase 0 only ships unit + e2e tests. The integration harness is in place so
Phase 1 can drop tests in without rearchitecting conftest.
"""
from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure test environment during collection.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://erp_admin:change_me@db:5432/erp_db_test")
os.environ.setdefault("DATABASE_URL_SYNC", "postgresql+psycopg://erp_admin:change_me@db:5432/erp_db_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-do-not-use-in-prod")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """HTTP client wired to the FastAPI app via ASGI transport (in-process)."""
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac