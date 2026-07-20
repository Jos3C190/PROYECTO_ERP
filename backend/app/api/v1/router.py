"""API v1 router aggregation.

Phase 0: health only. Phase 1: auth + me. Phase 1b: users CRUD (superuser-guarded).
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routers import auth, health, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/api/v1")
api_router.include_router(users.router, prefix="/api/v1")