"""SQLAlchemy AuditRepository — append-only (add + list only, no update/delete).

The architectural enforcement of append-only is twofold:
1. This class deliberately does NOT implement update() or delete() methods.
2. The API layer does not expose any UPDATE/DELETE endpoint for audit logs.
"""
from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, literal_column, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.audit import AuditLog as DomainLog
from app.infrastructure.models.audit import AuditLog as ORMLog


def _to_domain(orm: ORMLog) -> DomainLog:
    return DomainLog(
        id=orm.id,
        user_id=orm.user_id,
        action=orm.action,
        resource_type=orm.resource_type,
        resource_id=orm.resource_id,
        before_state=orm.before_state,
        after_state=orm.after_state,
        ip_address=orm.ip_address,
        user_agent=orm.user_agent,
        status=orm.status,
        metadata=orm.metadata_,
        created_at=orm.created_at,
    )


class SqlAlchemyAuditRepository:
    """Append-only: only add() and list() exist. No update/delete."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, log: DomainLog) -> DomainLog:
        orm = ORMLog(
            user_id=log.user_id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            before_state=log.before_state,
            after_state=log.after_state,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            status=log.status,
            metadata_=log.metadata,
        )
        self._session.add(orm)
        await self._session.flush()
        return _to_domain(orm)

    async def list(
        self,
        *,
        limit: int = 50,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[Sequence[DomainLog], bool]:
        """Keyset pagination over (created_at DESC, id DESC)."""
        conditions: list[Any] = []
        if cursor_created_at is not None and cursor_id is not None:
            # Strictly before the cursor row.
            conditions.append(
                or_clause(
                    ORMLog.created_at < cursor_created_at,
                    and_(ORMLog.created_at == cursor_created_at, ORMLog.id < cursor_id),
                )
            )
        if user_id is not None:
            conditions.append(ORMLog.user_id == user_id)
        if action is not None:
            conditions.append(ORMLog.action == action)
        if resource_type is not None:
            conditions.append(ORMLog.resource_type == resource_type)
        if resource_id is not None:
            conditions.append(ORMLog.resource_id == resource_id)
        if status is not None:
            conditions.append(ORMLog.status == status)
        if start_date is not None:
            conditions.append(ORMLog.created_at >= start_date)
        if end_date is not None:
            conditions.append(ORMLog.created_at <= end_date)

        stmt = select(ORMLog)
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.order_by(ORMLog.created_at.desc(), ORMLog.id.desc()).limit(limit + 1)

        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        has_more = len(rows) > limit
        items = rows[:limit]
        return [_to_domain(o) for o in items], has_more

    async def count(
        self,
        *,
        user_id: uuid.UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        conditions: list[Any] = []
        if user_id is not None:
            conditions.append(ORMLog.user_id == user_id)
        if action is not None:
            conditions.append(ORMLog.action == action)
        if resource_type is not None:
            conditions.append(ORMLog.resource_type == resource_type)
        if resource_id is not None:
            conditions.append(ORMLog.resource_id == resource_id)
        if status is not None:
            conditions.append(ORMLog.status == status)
        if start_date is not None:
            conditions.append(ORMLog.created_at >= start_date)
        if end_date is not None:
            conditions.append(ORMLog.created_at <= end_date)

        stmt = select(func.count(ORMLog.id))
        if conditions:
            stmt = stmt.where(*conditions)
        return int((await self._session.execute(stmt)).scalar_one())


def or_clause(*conditions: Any) -> Any:
    """Build an OR clause from conditions (SQLAlchemy 2.0 style)."""
    from sqlalchemy import or_

    return or_(*conditions)