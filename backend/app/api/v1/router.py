"""API v1 router aggregation.

Phase 0: only the root welcome + health. Phase 1+ will mount auth, users,
employees, roles, audit_log routers here.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routers import health

api_router = APIRouter()
api_router.include_router(health.router)