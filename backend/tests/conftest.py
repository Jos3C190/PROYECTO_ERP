"""Shared pytest fixtures.

We deliberately avoid a global DB fixture for unit tests. Integration tests opt
in with the `integration` marker and use the `db_session` fixture. E2E auth
tests use the `auth_app` fixture which boots the app with a real DB connection
and a per-test cleanup of the users table.
"""
from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure test environment during collection.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://erp_admin:change_me_in_production_please@db:5432/erp_db_test")
os.environ.setdefault("DATABASE_URL_SYNC", "postgresql+psycopg://erp_admin:change_me_in_production_please@db:5432/erp_db_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-do-not-use-in-prod")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """HTTP client wired to the FastAPI app via ASGI transport (in-process).
    Migrations are mocked so the app boots without a DB. Used for non-DB tests.
    """
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac