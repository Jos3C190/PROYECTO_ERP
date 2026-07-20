"""Phase 1 seed.

Idempotent: safe to re-run. Seeds:
- The SUPER_ADMIN user (credentials documented in README).
- A handful of demo users generated with Faker for pagination/search testing.

Permission catalogue and roles arrive in Phase 2 (RBAC). For now we only need
the super-admin so login works end-to-end.
"""
from __future__ import annotations

import asyncio
import os
import sys

import typer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure backend imports work when run via `python -m seed.seed_data`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = typer.Typer(add_completion=False, no_args_is_help=False)

SUPER_ADMIN_USERNAME = os.environ.get("SUPER_ADMIN_USERNAME", "superadmin")
SUPER_ADMIN_EMAIL = os.environ.get("SUPER_ADMIN_EMAIL", "superadmin@erp-system.dev")
SUPER_ADMIN_PASSWORD = os.environ.get(
    "SUPER_ADMIN_PASSWORD", "Cambio!Seguro2026"  # documented in README; must be rotated in prod
)


def _make_session_factory() -> async_sessionmaker[AsyncSession]:
    """Build a fresh engine + session factory bound to the current event loop.
    Avoids 'attached to a different loop' errors when the global factory was
    created during app startup in a different loop.
    """
    from app.core.config import settings

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
    return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def _seed_super_admin() -> None:
    from sqlalchemy import select

    from app.core.logging import configure_logging, get_logger
    from app.core.security import hash_password
    from app.infrastructure.models.user import User as ORMUser

    configure_logging()
    log = get_logger("seed")
    factory = _make_session_factory()

    async with factory() as session:
        existing = (
            await session.execute(
                select(ORMUser).where(ORMUser.username == SUPER_ADMIN_USERNAME)
            )
        ).scalar_one_or_none()

        if existing is not None:
            log.info("seed_super_admin_exists", username=SUPER_ADMIN_USERNAME)
            return

        orm = ORMUser(
            username=SUPER_ADMIN_USERNAME,
            email=SUPER_ADMIN_EMAIL,
            password_hash=hash_password(SUPER_ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True,
        )
        session.add(orm)
        await session.commit()
        log.info(
            "seed_super_admin_created",
            username=SUPER_ADMIN_USERNAME,
            email=SUPER_ADMIN_EMAIL,
        )


async def _seed_demo_users() -> None:
    """Generate demo users with Faker for pagination/search testing."""
    from sqlalchemy import select

    from app.core.logging import configure_logging, get_logger
    from app.core.security import hash_password
    from app.infrastructure.models.user import User as ORMUser

    configure_logging()
    log = get_logger("seed")
    fake = __import__("faker").Faker(["es_ES"])
    fake.seed_instance(42)
    password = hash_password("Demo!Usuario2026")
    factory = _make_session_factory()

    async with factory() as session:
        existing = (
            await session.execute(
                select(ORMUser).where(ORMUser.is_superuser.is_(False))
            )
        ).scalars().all()
        if len(existing) >= 25:
            log.info("seed_demo_users_skip", count=len(existing))
            return

        created = 0
        for _ in range(25):
            username = fake.unique.user_name()
            email = fake.unique.email()
            orm = ORMUser(
                username=username,
                email=email,
                password_hash=password,
                is_active=True,
                is_superuser=False,
            )
            session.add(orm)
            created += 1
        await session.commit()
        log.info("seed_demo_users_created", count=created)


@app.command()
def run(phase0: bool = typer.Option(False, "--phase0", help="Phase 0 placeholder mode.")) -> None:
    if phase0:
        typer.secho("[seed] Phase 0 — no seed data yet.", fg=typer.colors.CYAN)
        return

    typer.secho("[seed] Phase 1 — seeding super-admin and demo users...", fg=typer.colors.CYAN)
    asyncio.run(_seed_super_admin())
    asyncio.run(_seed_demo_users())
    typer.secho(
        f"[seed] Done. SUPER_ADMIN = {SUPER_ADMIN_USERNAME} / {SUPER_ADMIN_PASSWORD}",
        fg=typer.colors.GREEN,
    )


if __name__ == "__main__":
    app()