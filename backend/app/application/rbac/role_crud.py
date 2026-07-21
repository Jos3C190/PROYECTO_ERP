"""Use cases: role CRUD + permission matrix assignment."""
from __future__ import annotations

import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.core.logging import get_logger
from app.domain.entities.rbac import Permission, Role
from app.domain.ports.permission_repository import PermissionRepository
from app.domain.ports.role_repository import RoleRepository

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class CreateRoleInput:
    name: str
    description: str | None = None


class CreateRoleUseCase:
    def __init__(self, roles: RoleRepository) -> None:
        self._roles = roles

    async def execute(self, inp: CreateRoleInput) -> Role:
        if await self._roles.get_by_name(inp.name):
            raise ConflictError("El nombre de rol ya existe.", code="role_name_taken")
        new_role = Role(
            id=uuid.uuid4(),
            name=inp.name,
            description=inp.description,
            is_system=False,
        )
        created = await self._roles.add(new_role)
        log.info("role_created", role_id=str(created.id), name=created.name)
        return created


@dataclass(frozen=True, slots=True)
class UpdateRoleInput:
    role_id: uuid.UUID
    name: str | None = None
    description: str | None = None


class UpdateRoleUseCase:
    def __init__(self, roles: RoleRepository) -> None:
        self._roles = roles

    async def execute(self, inp: UpdateRoleInput) -> Role:
        role = await self._roles.get_by_id(inp.role_id)
        if role is None:
            raise NotFoundError("Rol no encontrado.", code="role_not_found")

        if inp.name and inp.name != role.name:
            if await self._roles.get_by_name(inp.name):
                raise ConflictError("El nombre de rol ya existe.", code="role_name_taken")

        updated = Role(
            id=role.id,
            name=inp.name or role.name,
            description=inp.description if inp.description is not None else role.description,
            is_system=role.is_system,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=role.permissions,
        )
        result = await self._roles.update(updated)
        log.info("role_updated", role_id=str(role.id))
        return result


class DeleteRoleUseCase:
    def __init__(self, roles: RoleRepository) -> None:
        self._roles = roles

    async def execute(self, role_id: uuid.UUID) -> bool:
        role = await self._roles.get_by_id(role_id)
        if role is None:
            raise NotFoundError("Rol no encontrado.", code="role_not_found")
        if role.is_system:
            raise BusinessRuleError(
                "Los roles de sistema no pueden eliminarse.", code="system_role_protected"
            )
        ok = await self._roles.delete(role_id)
        if ok:
            log.info("role_deleted", role_id=str(role_id))
        return ok


@dataclass(frozen=True, slots=True)
class SetRolePermissionsInput:
    role_id: uuid.UUID
    permission_codes: tuple[str, ...]


class SetRolePermissionsUseCase:
    def __init__(self, roles: RoleRepository, permissions: PermissionRepository) -> None:
        self._roles = roles
        self._permissions = permissions

    async def execute(self, inp: SetRolePermissionsInput) -> Role:
        role = await self._roles.get_by_id(inp.role_id, load_permissions=True)
        if role is None:
            raise NotFoundError("Rol no encontrado.", code="role_not_found")

        # Resolve codes -> ids, validating each one exists.
        perm_ids: set[uuid.UUID] = set()
        all_perms = {p.code: p.id for p in await self._permissions.list_all()}
        for code in inp.permission_codes:
            if code not in all_perms:
                raise BusinessRuleError(
                    f"Permiso desconocido: {code}", code="unknown_permission"
                )
            perm_ids.add(all_perms[code])

        await self._roles.set_permissions(role.id, perm_ids)
        log.info(
            "role_permissions_set",
            role_id=str(role.id),
            count=len(perm_ids),
        )
        # Return updated role with permissions loaded
        return await self._roles.get_by_id(role.id, load_permissions=True) or role


class ListRolesUseCase:
    def __init__(self, roles: RoleRepository) -> None:
        self._roles = roles

    async def execute(self, *, load_permissions: bool = False) -> Sequence[Role]:
        return await self._roles.list_all(load_permissions=load_permissions)


class GetRoleUseCase:
    def __init__(self, roles: RoleRepository) -> None:
        self._roles = roles

    async def execute(self, role_id: uuid.UUID) -> Role:
        role = await self._roles.get_by_id(role_id, load_permissions=True)
        if role is None:
            raise NotFoundError("Rol no encontrado.", code="role_not_found")
        return role


class ListPermissionsUseCase:
    def __init__(self, permissions: PermissionRepository) -> None:
        self._permissions = permissions

    async def execute(self) -> Sequence[Permission]:
        return await self._permissions.list_all()