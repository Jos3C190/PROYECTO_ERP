"""Roles router — CRUD + permission matrix + user-role assignment.

All endpoints require `permissions:read` or `roles:*` permissions via
`require_permission`. Superusers pass automatically.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import (
    CurrentUser,
    SessionDep,
    get_permission_repository,
    get_role_repository,
    get_user_repository,
    require_permission,
)
from app.api.v1.schemas.common import MessageOut
from app.api.v1.schemas.rbac import (
    AssignRoleRequest,
    CreateRoleRequest,
    EffectivePermissionsOut,
    PermissionOut,
    RevokeRoleRequest,
    RoleOut,
    RoleWithPermissionsOut,
    SetRolePermissionsRequest,
    UpdateRoleRequest,
    UserRoleAssignmentOut,
)
from app.application.rbac.check_permission import GetEffectivePermissionsUseCase
from app.application.rbac.role_assignment import (
    AssignRoleInput,
    AssignRoleUseCase,
    GetUserRolesUseCase,
    RevokeRoleInput,
    RevokeRoleUseCase,
)
from app.application.rbac.role_crud import (
    CreateRoleInput,
    CreateRoleUseCase,
    DeleteRoleUseCase,
    GetRoleUseCase,
    ListPermissionsUseCase,
    ListRolesUseCase,
    SetRolePermissionsInput,
    SetRolePermissionsUseCase,
    UpdateRoleInput,
    UpdateRoleUseCase,
)
from app.domain.ports.permission_repository import PermissionRepository
from app.domain.ports.role_repository import RoleRepository
from app.domain.ports.user_repository import UserRepository

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get(
    "",
    response_model=list[RoleWithPermissionsOut],
    status_code=status.HTTP_200_OK,
    summary="Listar roles (con permisos)",
    dependencies=[Depends(require_permission("roles:read"))],
)
async def list_roles(
    repo: RoleRepository = Depends(get_role_repository),
) -> list[RoleWithPermissionsOut]:
    uc = ListRolesUseCase(repo)
    roles = await uc.execute(load_permissions=True)
    return [
        RoleWithPermissionsOut(
            id=r.id,
            name=r.name,
            description=r.description,
            is_system=r.is_system,
            created_at=r.created_at or __import__("datetime").datetime.now(),
            updated_at=r.updated_at,
            permissions=[
                PermissionOut(
                    id=p.id, code=p.code, description=p.description, module=p.module
                )
                for p in r.permissions
            ],
        )
        for r in roles
    ]


@router.get(
    "/permissions",
    response_model=list[PermissionOut],
    status_code=status.HTTP_200_OK,
    summary="Catálogo de permisos",
    dependencies=[Depends(require_permission("permissions:read"))],
)
async def list_permissions(
    repo: PermissionRepository = Depends(get_permission_repository),
) -> list[PermissionOut]:
    uc = ListPermissionsUseCase(repo)
    perms = await uc.execute()
    return [
        PermissionOut(id=p.id, code=p.code, description=p.description, module=p.module)
        for p in perms
    ]


@router.get(
    "/{role_id}",
    response_model=RoleWithPermissionsOut,
    status_code=status.HTTP_200_OK,
    summary="Obtener rol por id (con permisos)",
    dependencies=[Depends(require_permission("roles:read"))],
)
async def get_role(
    role_id: uuid.UUID,
    repo: RoleRepository = Depends(get_role_repository),
) -> RoleWithPermissionsOut:
    uc = GetRoleUseCase(repo)
    r = await uc.execute(role_id)
    return RoleWithPermissionsOut(
        id=r.id,
        name=r.name,
        description=r.description,
        is_system=r.is_system,
        created_at=r.created_at or __import__("datetime").datetime.now(),
        updated_at=r.updated_at,
        permissions=[
            PermissionOut(id=p.id, code=p.code, description=p.description, module=p.module)
            for p in r.permissions
        ],
    )


@router.post(
    "",
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear rol",
    dependencies=[Depends(require_permission("roles:create"))],
)
async def create_role(
    body: CreateRoleRequest,
    repo: RoleRepository = Depends(get_role_repository),
) -> RoleOut:
    uc = CreateRoleUseCase(repo)
    r = await uc.execute(CreateRoleInput(name=body.name, description=body.description))
    return RoleOut(
        id=r.id,
        name=r.name,
        description=r.description,
        is_system=r.is_system,
        created_at=r.created_at or __import__("datetime").datetime.now(),
        updated_at=r.updated_at,
    )


@router.patch(
    "/{role_id}",
    response_model=RoleOut,
    status_code=status.HTTP_200_OK,
    summary="Actualizar rol",
    dependencies=[Depends(require_permission("roles:update"))],
)
async def update_role(
    role_id: uuid.UUID,
    body: UpdateRoleRequest,
    repo: RoleRepository = Depends(get_role_repository),
) -> RoleOut:
    uc = UpdateRoleUseCase(repo)
    r = await uc.execute(
        UpdateRoleInput(role_id=role_id, name=body.name, description=body.description)
    )
    return RoleOut(
        id=r.id,
        name=r.name,
        description=r.description,
        is_system=r.is_system,
        created_at=r.created_at or __import__("datetime").datetime.now(),
        updated_at=r.updated_at,
    )


@router.delete(
    "/{role_id}",
    response_model=MessageOut,
    status_code=status.HTTP_200_OK,
    summary="Eliminar rol (no sistema)",
    dependencies=[Depends(require_permission("roles:delete"))],
)
async def delete_role(
    role_id: uuid.UUID,
    repo: RoleRepository = Depends(get_role_repository),
) -> MessageOut:
    uc = DeleteRoleUseCase(repo)
    await uc.execute(role_id)
    return MessageOut(message="Rol eliminado.", code="role_deleted")


@router.put(
    "/{role_id}/permissions",
    response_model=RoleWithPermissionsOut,
    status_code=status.HTTP_200_OK,
    summary="Asignar permisos a un rol (matriz)",
    dependencies=[Depends(require_permission("permissions:manage"))],
)
async def set_role_permissions(
    role_id: uuid.UUID,
    body: SetRolePermissionsRequest,
    repo: RoleRepository = Depends(get_role_repository),
    perm_repo: PermissionRepository = Depends(get_permission_repository),
) -> RoleWithPermissionsOut:
    uc = SetRolePermissionsUseCase(repo, perm_repo)
    r = await uc.execute(
        SetRolePermissionsInput(role_id=role_id, permission_codes=tuple(body.permission_codes))
    )
    return RoleWithPermissionsOut(
        id=r.id,
        name=r.name,
        description=r.description,
        is_system=r.is_system,
        created_at=r.created_at or __import__("datetime").datetime.now(),
        updated_at=r.updated_at,
        permissions=[
            PermissionOut(id=p.id, code=p.code, description=p.description, module=p.module)
            for p in r.permissions
        ],
    )


@router.post(
    "/assign",
    response_model=MessageOut,
    status_code=status.HTTP_200_OK,
    summary="Asignar rol a usuario",
    dependencies=[Depends(require_permission("roles:assign"))],
)
async def assign_role(
    body: AssignRoleRequest,
    current: CurrentUser,
    repo: RoleRepository = Depends(get_role_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> MessageOut:
    uc = AssignRoleUseCase(user_repo, repo)
    created = await uc.execute(
        AssignRoleInput(user_id=body.user_id, role_id=body.role_id, assigned_by=current.id)
    )
    return MessageOut(
        message="Rol asignado." if created else "El usuario ya tenía ese rol.",
        code="role_assigned" if created else "role_already_assigned",
    )


@router.post(
    "/revoke",
    response_model=MessageOut,
    status_code=status.HTTP_200_OK,
    summary="Revocar rol de usuario",
    dependencies=[Depends(require_permission("roles:revoke"))],
)
async def revoke_role(
    body: RevokeRoleRequest,
    current: CurrentUser,
    repo: RoleRepository = Depends(get_role_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> MessageOut:
    uc = RevokeRoleUseCase(user_repo, repo)
    ok = await uc.execute(
        RevokeRoleInput(user_id=body.user_id, role_id=body.role_id, actor_id=current.id)
    )
    return MessageOut(
        message="Rol revocado." if ok else "El usuario no tenía ese rol.",
        code="role_revoked" if ok else "role_not_assigned",
    )


@router.get(
    "/users/{user_id}/roles",
    response_model=list[RoleOut],
    status_code=status.HTTP_200_OK,
    summary="Roles asignados a un usuario",
    dependencies=[Depends(require_permission("roles:read"))],
)
async def get_user_roles(
    user_id: uuid.UUID,
    repo: RoleRepository = Depends(get_role_repository),
) -> list[RoleOut]:
    uc = GetUserRolesUseCase(repo)
    roles = await uc.execute(user_id)
    return [
        RoleOut(
            id=r.id,
            name=r.name,
            description=r.description,
            is_system=r.is_system,
            created_at=r.created_at or __import__("datetime").datetime.now(),
            updated_at=r.updated_at,
        )
        for r in roles
    ]


# Separate router mounted at /auth/me/permissions to keep the path natural.
me_router = APIRouter(prefix="/auth", tags=["auth"])


@me_router.get(
    "/me/permissions",
    response_model=EffectivePermissionsOut,
    status_code=status.HTTP_200_OK,
    summary="Permisos efectivos del usuario actual",
)
async def my_permissions(
    current: CurrentUser,
    user_repo: UserRepository = Depends(get_user_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
) -> EffectivePermissionsOut:
    uc = GetEffectivePermissionsUseCase(user_repo, role_repo)
    perms = await uc.execute(current.id)
    if perms == ("*",):
        from app.application.rbac.catalogue import ALL_PERMISSION_CODES

        return EffectivePermissionsOut(
            permissions=sorted(ALL_PERMISSION_CODES), is_superuser=True
        )
    return EffectivePermissionsOut(permissions=list(perms), is_superuser=False)