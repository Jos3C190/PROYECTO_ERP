"""Dependency providers for the API layer.

Centralising providers here keeps routers thin and makes testing trivial: tests
override a single dependency to swap a real repo for an in-memory fake.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_async_session

# Type aliases used widely in routers.
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


__all__ = ["SessionDep"]