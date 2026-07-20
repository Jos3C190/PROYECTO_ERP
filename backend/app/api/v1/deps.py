"""Dependency providers for the API layer.

Centralising providers here keeps routers thin and makes testing trivial: tests
override a single dependency to swap a real repo for an in-memory fake.
"""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.get_current_user import GetCurrentUserUseCase
from app.application.auth.authenticate_user import AuthenticateUserUseCase
from app.application.auth.logout import LogoutUseCase
from app.application.auth.refresh_token import RefreshTokenUseCase
from app.application.auth.register_user import RegisterUserUseCase
from app.application.password_policy import PasswordPolicy
from app.core.exceptions import AuthenticationError
from app.domain.entities.user import User
from app.domain.ports.refresh_token_repository import RefreshTokenRepository
from app.domain.ports.token_service import TokenService
from app.domain.ports.user_repository import UserRepository
from app.infrastructure.db.session import get_async_session
from app.infrastructure.repositories import (
    JwtTokenService,
    SqlAlchemyRefreshTokenRepository,
    SqlAlchemyUserRepository,
)

# Type aliases used widely in routers.
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

_bearer = HTTPBearer(auto_error=False)


# -------- repository / service factories --------
def get_user_repository(session: SessionDep) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_refresh_token_repository(session: SessionDep) -> RefreshTokenRepository:
    return SqlAlchemyRefreshTokenRepository(session)


def get_token_service() -> TokenService:
    return JwtTokenService()


def get_password_policy() -> PasswordPolicy:
    return PasswordPolicy()


# -------- use case providers --------
def get_authenticate_user_use_case(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    sessions: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(users, sessions, tokens)


def get_refresh_token_use_case(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    sessions: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(users, sessions, tokens)


def get_logout_use_case(
    sessions: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
) -> LogoutUseCase:
    return LogoutUseCase(sessions, tokens)


def get_register_user_use_case(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    policy: Annotated[PasswordPolicy, Depends(get_password_policy)],
) -> RegisterUserUseCase:
    return RegisterUserUseCase(users, policy)


def get_current_user_use_case(
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(users)


# -------- authenticated user dependency --------
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """Resolve the Bearer token to a User. Raises 401 if missing/invalid."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("No autenticado.", code="not_authenticated")
    payload = tokens.verify_access_token(credentials.credentials)
    use_case = GetCurrentUserUseCase(users)
    result = await use_case.execute(payload.sub)
    return result.user


CurrentUser = Annotated[User, Depends(get_current_user)]


__all__ = [
    "SessionDep",
    "CurrentUser",
    "get_current_user",
    "get_user_repository",
    "get_refresh_token_repository",
    "get_token_service",
    "get_password_policy",
    "get_authenticate_user_use_case",
    "get_refresh_token_use_case",
    "get_logout_use_case",
    "get_register_user_use_case",
    "get_current_user_use_case",
]