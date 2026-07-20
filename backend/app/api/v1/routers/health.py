"""Health endpoints.

- `/health/live`  : process is alive (no I/O). For orchestrator liveness probes.
- `/health/ready` : can serve requests (checks DB roundtrip). For readiness probes.
- `/health`       : same as ready, plus component breakdown.

These are deliberately NOT under `/api/v1` so they sit at the root and match
typical probe expectations. They are also registered in `main.py` separately.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, status
from sqlalchemy import text

from app.api.v1.deps import SessionDep
from app.api.v1.schemas.common import HealthComponent, HealthReport
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/live", summary="Liveness probe", status_code=status.HTTP_200_OK)
async def live() -> HealthReport:
    return HealthReport(
        status="ok",
        version=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        timestamp=_now(),
        components=[HealthComponent(name="process", status="ok")],
    )


@router.get("/ready", summary="Readiness probe", status_code=status.HTTP_200_OK)
async def ready(session: SessionDep) -> HealthReport:
    db_status = "ok"
    detail: str | None = None
    try:
        result = await session.execute(text("SELECT 1"))
        _ = result.scalar_one()
    except Exception as exc:  # noqa: BLE001
        db_status = "down"
        detail = str(exc)[:200]

    overall = "ok" if db_status == "ok" else "degraded"
    return HealthReport(
        status=overall,
        version=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        timestamp=_now(),
        components=[HealthComponent(name="database", status=db_status, detail=detail)],
    )


@router.get("", summary="Full health report", status_code=status.HTTP_200_OK)
async def health(session: SessionDep) -> HealthReport:
    return await ready(session)  # type: ignore[arg-type]