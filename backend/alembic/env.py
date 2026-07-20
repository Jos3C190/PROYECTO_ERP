"""Alembic environment. Supports offline (sql), online-async (asyncpg) and
online-sync (psycopg) modes.

The app's startup migration runner passes the SYNC url (`postgresql://...`)
and runs `command.upgrade` in a thread, so alembic lands here in sync-online
mode. When `alembic upgrade` is invoked manually with the async URL, the
async-online path is used. Offline mode (`alembic upgrade --sql`) emits SQL
without a connection.
"""
from __future__ import annotations

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Make `app` importable when running `alembic` from the backend/ dir.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402
from app.infrastructure.db.base import Base  # noqa: E402
# Importing the models package registers every ORM table on Base.metadata.
from app.infrastructure import models as _models  # noqa: F401, E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Prefer the sync URL if set (the app startup uses it); fall back to the async URL.
_url = os.environ.get("DATABASE_URL_SYNC") or settings.DATABASE_URL_SYNC or settings.DATABASE_URL
config.set_main_option("sqlalchemy.url", _url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Offline mode: emit SQL to stdout without a live connection."""
    context.configure(
        url=_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _is_async_url(url: str) -> bool:
    return "+asyncpg" in url


def run_migrations_online_sync() -> None:
    from sqlalchemy import create_engine

    engine = create_engine(_url, poolclass=pool.NullPool, future=True)
    try:
        with engine.connect() as connection:
            do_run_migrations(connection)
    finally:
        engine.dispose()


async def run_migrations_online_async() -> None:
    connectable = async_engine_from_config(
        {"sqlalchemy.url": _url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    if _is_async_url(_url):
        asyncio.run(run_migrations_online_async())
    else:
        run_migrations_online_sync()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()