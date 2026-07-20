"""User management DTOs."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.api.v1.schemas.common import ORMOut, Page, PageMeta  # re-export for router convenience


class UserOut(ORMOut):
    id: uuid.UUID
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    mfa_enabled: bool
    last_login_at: datetime | None = None
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    password_changed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    is_superuser: bool = False


class UpdateUserRequest(BaseModel):
    is_active: bool | None = None
    is_superuser: bool | None = None


class ForcePasswordResetRequest(BaseModel):
    new_password: str = Field(..., min_length=12, max_length=128)


class MessageOut(BaseModel):
    message: str
    code: str | None = None


__all__ = [
    "UserOut",
    "Page",
    "PageMeta",
    "CreateUserRequest",
    "UpdateUserRequest",
    "ForcePasswordResetRequest",
    "MessageOut",
]