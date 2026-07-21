"""Audit log router — read-only with page-based pagination.

Only GET endpoints. No POST/PUT/PATCH/DELETE — the audit log is append-only
and entries are created internally by AuditService during business operations.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.deps import SessionDep, require_permission
from app.api.v1.schemas.audit import AuditLogOut, AuditLogPage
from app.api.v1.schemas.common import PageMeta
from app.domain.ports.audit_repository import AuditRepository

router = APIRouter(prefix="/audit-logs", tags=["audit"])


def _get_audit_repo(session: SessionDep) -> AuditRepository:
    from app.infrastructure.repositories import SqlAlchemyAuditRepository

    return SqlAlchemyAuditRepository(session)


@router.get(
    "",
    response_model=AuditLogPage,
    status_code=status.HTTP_200_OK,
    summary="Listar bitácora (paginado)",
    dependencies=[Depends(require_permission("audit_log:read"))],
)
async def list_audit_logs(
    repo: AuditRepository = Depends(_get_audit_repo),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    user_id: uuid.UUID | None = Query(None),
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
    resource_id: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
) -> AuditLogPage:
    offset = (page - 1) * size

    logs, _has_more = await repo.list(
        limit=size,
        offset=offset,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
    )

    total = await repo.count(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
    )

    pages = (total + size - 1) // size if total else 1

    items = [
        AuditLogOut(
            id=l.id,
            user_id=l.user_id,
            action=l.action,
            resource_type=l.resource_type,
            resource_id=l.resource_id,
            before_state=l.before_state,
            after_state=l.after_state,
            ip_address=l.ip_address,
            user_agent=l.user_agent,
            status=l.status,
            metadata=l.metadata,
            created_at=l.created_at or datetime.now(timezone.utc),
        )
        for l in logs
    ]

    return AuditLogPage(
        items=items,
        meta=PageMeta(page=page, size=size, total=total, pages=pages),
    )