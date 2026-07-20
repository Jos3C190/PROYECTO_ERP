"""Auth DTOs (login, token, user out)."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.api.v1.schemas.common import ORMOut


class LoginRequest(BaseModel):
    login: str = Field(..., min_length=3, max_length=320, description="Email o nombre de usuario.")
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Segundos hasta la expiración del access token.")
    refresh_token: str = Field(..., description="Refresh token raw (se devuelve solo una vez).")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10, max_length=128)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10, max_length=128)


class UserOut(ORMOut):
    id: uuid.UUID
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    mfa_enabled: bool
    last_login_at: datetime | None = None
    failed_login_attempts: int
    locked_until: datetime | None = None
    created_at: datetime
    updated_at: datetime


class MeResponse(UserOut):
    """Alias for /me — same fields as UserOut, semantically the current user."""


class MessageOut(BaseModel):
    message: str
    code: str | None = None