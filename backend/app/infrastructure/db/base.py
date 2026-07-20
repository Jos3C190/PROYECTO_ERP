"""Declarative base + shared mixins for ORM models.

Design choices (per master prompt section 4):
- UUID primary keys (no autoincrement int) to avoid enumeration + ease sharding.
- `created_at`, `updated_at` on every entity.
- `deleted_at` for soft-delete on business entities.
- Naming convention for constraints so Alembic autogenerate produces stable names.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base. All ORM models subclass this."""

    metadata: Any  # type: ignore[assignment]


class UUIDPKMixin:
    """UUID primary key, server-side gen_random_uuid()."""

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        sort_order=-999,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None