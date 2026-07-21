"""API v1 router aggregation.

Phase 0: health. Phase 1: auth + me. Phase 1b: users CRUD. Phase 2: RBAC.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routers import auth, health, roles, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/api/v1")
api_router.include_router(users.router, prefix="/api/v1")
api_router.include_router(roles.router, prefix="/api/v1")
api_router.include_router(roles.me_router, prefix="/api/v1")