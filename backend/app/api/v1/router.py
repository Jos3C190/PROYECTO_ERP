"""API v1 router aggregation.

Phase 0: health only. Phase 1: auth + me.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routers import auth, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/api/v1")