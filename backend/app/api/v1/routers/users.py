"""Users router — admin CRUD for user management.

Phase 1b: guarded by `is_superuser` (the actor must be a superadmin). Phase 2
replaces this with the dynamic RBAC `require_permission` dependency.

Business rules enforced in the use cases:
- Cannot self-deactivate or self-demote.
- Cannot remove the last active superadmin.
- Force-reset not allowed on self.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.api.v1.deps import CurrentUser, SessionDep, get_register_user_use_case
from app.api.v1.schemas.common import MessageOut
from app.api.v1.schemas.users import (
    CreateUserRequest,
    ForcePasswordResetRequest,
    Page,
    PageMeta,
    UpdateUserRequest,
    UserOut,
)
from app.application.auth.register_user import (
    RegisterUserInput,
    RegisterUserUseCase,
)
from app.application.users.admin_actions import (
    DeactivateUserUseCase,
    ForcePasswordResetInput,
    ForcePasswordResetUseCase,
    UnlockAccountUseCase,
)
from app.application.users.get_user import GetUserUseCase
from app.application.users.list_users import ListUsersInput, ListUsersUseCase
from app.application.users.update_user import UpdateUserInput, UpdateUserUseCase
from app.core.exceptions import AuthorizationError
from app.domain.ports.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["users"])


def require_superuser(current: CurrentUser) -> None:
    """Phase 1b guard. Phase 2 replaces with RBAC require_permission."""
    if not current.is_superuser:
        raise AuthorizationError(
            "Requiere privilegios de superadministrador.", code="superuser_required"
        )


def _get_user_repo(session: SessionDep) -> UserRepository:
    from app.infrastructure.repositories import SqlAlchemyUserRepository

    return SqlAlchemyUserRepository(session)


@router.get(
    "",
    response_model=Page[UserOut],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios (paginado)",
)
async def list_users(
    current: CurrentUser,
    _guard: None = Depends(require_superuser),
    repo: UserRepository = Depends(_get_user_repo),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=120),
) -> Page[UserOut]:
    uc = ListUsersUseCase(repo)
    result = await uc.execute(ListUsersInput(page=page, size=size, search=search))
    return Page[UserOut](
        items=[UserOut.model_validate(u, from_attributes=True) for u in result.items],
        meta=PageMeta(page=result.page, size=result.size, total=result.total, pages=result.pages),
    )


@router.get(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario por id",
)
async def get_user(
    user_id: uuid.UUID,
    current: CurrentUser,
    _guard: None = Depends(require_superuser),
    repo: UserRepository = Depends(_get_user_repo),
) -> UserOut:
    uc = GetUserUseCase(repo)
    result = await uc.execute(user_id)
    return UserOut.model_validate(result.user, from_attributes=True)


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
)
async def create_user(
    body: CreateUserRequest,
    current: CurrentUser,
    _guard: None = Depends(require_superuser),
    register_uc: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> UserOut:
    created = await register_uc.execute(
        RegisterUserInput(
            username=body.username,
            email=body.email,
            password=body.password,
            is_active=True,
            is_superuser=body.is_superuser,
        )
    )
    return UserOut.model_validate(created, from_attributes=True)


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario (activo / superadmin)",
)
async def update_user(
    user_id: uuid.UUID,
    body: UpdateUserRequest,
    current: CurrentUser,
    _guard: None = Depends(require_superuser),
    repo: UserRepository = Depends(_get_user_repo),
) -> UserOut:
    uc = UpdateUserUseCase(repo)
    updated = await uc.execute(
        UpdateUserInput(
            target_id=user_id,
            actor_id=current.id,
            is_active=body.is_active,
            is_superuser=body.is_superuser,
        )
    )
    return UserOut.model_validate(updated, from_attributes=True)


@router.post(
    "/{user_id}/force-password-reset",
    response_model=MessageOut,
    status_code=status.HTTP_200_OK,
    summary="Forzar cambio de contraseña",
)
async def force_password_reset(
    user_id: uuid.UUID,
    body: ForcePasswordResetRequest,
    current: CurrentUser,
    _guard: None = Depends(require_superuser),
    repo: UserRepository = Depends(_get_user_repo),
) -> MessageOut:
    uc = ForcePasswordResetUseCase(repo)
    await uc.execute(
        ForcePasswordResetInput(
            target_id=user_id, actor_id=current.id, new_password=body.new_password
        )
    )
    return MessageOut(message="Contraseña actualizada.", code="password_reset")


@router.post(
    "/{user_id}/unlock",
    response_model=MessageOut,
    status_code=status.HTTP_200_OK,
    summary="Desbloquear cuenta",
)
async def unlock_account(
    user_id: uuid.UUID,
    current: CurrentUser,
    _guard: None = Depends(require_superuser),
    repo: UserRepository = Depends(_get_user_repo),
) -> MessageOut:
    uc = UnlockAccountUseCase(repo)
    await uc.execute(user_id)
    return MessageOut(message="Cuenta desbloqueada.", code="account_unlocked")


@router.delete(
    "/{user_id}",
    response_model=MessageOut,
    status_code=status.HTTP_200_OK,
    summary="Desactivar usuario (soft delete)",
)
async def deactivate_user(
    user_id: uuid.UUID,
    current: CurrentUser,
    _guard: None = Depends(require_superuser),
    repo: UserRepository = Depends(_get_user_repo),
) -> MessageOut:
    uc = DeactivateUserUseCase(repo)
    await uc.execute(user_id, current.id)
    return MessageOut(message="Usuario desactivado.", code="user_deactivated")