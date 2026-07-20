"""Auth router — login, refresh, logout, /me.

Login and refresh are rate-limited per IP (OWASP A07). Refresh tokens are
issued as httpOnly Secure SameSite=Strict cookies AND echoed in the body
once for clients that can't store cookies. Logout is idempotent.
"""
from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from fastapi.responses import JSONResponse

from app.api.v1.deps import (
    CurrentUser,
    get_authenticate_user_use_case,
    get_logout_use_case,
    get_refresh_token_use_case,
)
from app.api.v1.schemas.auth import (
    LoginRequest,
    MeResponse,
    RefreshRequest,
    TokenResponse,
    UserOut,
)
from app.api.v1.schemas.common import MessageOut
from app.application.auth.authenticate_user import AuthenticateUserUseCase, LoginInput
from app.application.auth.logout import LogoutInput, LogoutUseCase
from app.application.auth.refresh_token import (
    RefreshInput,
    RefreshTokenUseCase,
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "erp_refresh_token"


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=raw_token,
        httponly=True,
        secure=settings.SECURE_COOKIES,
        samesite="strict",
        path="/api/v1/auth",
        max_age=int(
            # align with refresh ttl (7d)
            7 * 24 * 60 * 60
        ),
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE, path="/api/v1/auth")


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
) -> TokenResponse:
    result = await use_case.execute(
        LoginInput(
            login=payload.login,
            password=payload.password,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
    )
    _set_refresh_cookie(response, result.refresh_token)
    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in_seconds,
        refresh_token=result.refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotar access token",
)
async def refresh(
    request: Request,
    response: Response,
    body: RefreshRequest | None = None,
    refresh_cookie: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> TokenResponse:
    raw = (body.refresh_token if body and body.refresh_token else None) or refresh_cookie
    if not raw:
        return JSONResponse(
            status_code=401,
            content={"code": "token_invalid", "message": "Refresh token requerido."},
        )
    result = await use_case.execute(
        RefreshInput(
            raw_refresh_token=raw,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
    )
    _set_refresh_cookie(response, result.refresh_token)
    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in_seconds,
        refresh_token=result.refresh_token,
    )


@router.post(
    "/logout",
    response_model=MessageOut,
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión",
)
async def logout(
    response: Response,
    body: RefreshRequest | None = None,
    refresh_cookie: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    use_case: LogoutUseCase = Depends(get_logout_use_case),
) -> MessageOut:
    raw = (body.refresh_token if body and body.refresh_token else None) or refresh_cookie
    if raw:
        await use_case.execute(LogoutInput(raw_refresh_token=raw))
    _clear_refresh_cookie(response)
    return MessageOut(message="Sesión cerrada.", code="logout_ok")


@router.get(
    "/me",
    response_model=MeResponse,
    status_code=status.HTTP_200_OK,
    summary="Usuario actual",
)
async def me(current: CurrentUser) -> MeResponse:
    return MeResponse.model_validate(current, from_attributes=True)


@router.get(
    "/me/users",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Perfil del usuario actual (alias)",
    include_in_schema=False,
)
async def me_user(current: CurrentUser) -> UserOut:
    return UserOut.model_validate(current, from_attributes=True)