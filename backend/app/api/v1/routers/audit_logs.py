"""Audit log router — read-only with keyset (cursor) pagination.

Only GET endpoints. No POST/PUT/PATCH/DELETE — the audit log is append-only
and entries are created internally by AuditService during business operations.
"""
from __future__ import annotations

import base64
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.deps import SessionDep, require_permission
from app.api.v1.schemas.audit import AuditLogOut, AuditLogPage
from app.domain.ports.audit_repository import AuditRepository

router = APIRouter(prefix="/audit-logs", tags=["audit"])


def _get_audit_repo(session: SessionDep) -> AuditRepository:
    from app.infrastructure.repositories import SqlAlchemyAuditRepository

    return SqlAlchemyAuditRepository(session)


def _encode_cursor(created_at: datetime, log_id: uuid.UUID) -> str:
    payload = json.dumps(
        {"created_at": created_at.isoformat(), "id": str(log_id)},
        separators=(",", ":"),
    )
    return base64.b64encode(payload.encode()).decode()


def _decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    payload = json.loads(base64.b64decode(cursor.encode()))
    return datetime.fromisoformat(payload["created_at"]), uuid.UUID(payload["id"])


@router.get(
    "",
    response_model=AuditLogPage,
    status_code=status.HTTP_200_OK,
    summary="Listar bitácora (cursor pagination)",
    dependencies=[Depends(require_permission("audit_log:read"))],
)
async def list_audit_logs(
    repo: AuditRepository = Depends(_get_audit_repo),
    limit: int = Query(50, ge=1, le=200),
    cursor: str | None = Query(None, description="Cursor codificado de la página anterior"),
    user_id: uuid.UUID | None = Query(None),
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
    resource_id: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
) -> AuditLogPage:
    cursor_created_at: datetime | None = None
    cursor_id: uuid.UUID | None = None
    if cursor:
        try:
            cursor_created_at, cursor_id = _decode_cursor(cursor)
        except Exception:
            pass  # ignore invalid cursor, start from beginning

    logs, has_more = await repo.list(
        limit=limit,
        cursor_created_at=cursor_created_at,
        cursor_id=cursor_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
    )

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

    next_cursor: str | None = None
    if has_more and items:
        last = items[-1]
        next_cursor = _encode_cursor(last.created_at, last.id)

    return AuditLogPage(items=items, next_cursor=next_cursor, has_more=has_more)