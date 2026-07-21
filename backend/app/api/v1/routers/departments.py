"""Departments router — CRUD + hierarchy."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import SessionDep, require_permission
from app.api.v1.schemas.common import MessageOut
from app.api.v1.schemas.employees import (
    CreateDepartmentRequest,
    DepartmentOut,
    UpdateDepartmentRequest,
)
from app.application.employees.department_crud import (
    CreateDepartmentInput,
    CreateDepartmentUseCase,
    DeleteDepartmentUseCase,
    GetDepartmentUseCase,
    ListDepartmentsUseCase,
    UpdateDepartmentInput,
    UpdateDepartmentUseCase,
)
from app.domain.ports.department_repository import DepartmentRepository

router = APIRouter(prefix="/departments", tags=["departments"])


def _get_dept_repo(session: SessionDep) -> DepartmentRepository:
    from app.infrastructure.repositories import SqlAlchemyDepartmentRepository

    return SqlAlchemyDepartmentRepository(session)


@router.get(
    "",
    response_model=list[DepartmentOut],
    status_code=status.HTTP_200_OK,
    summary="Listar departamentos",
    dependencies=[Depends(require_permission("employees:read"))],
)
async def list_departments(
    repo: DepartmentRepository = Depends(_get_dept_repo),
) -> list[DepartmentOut]:
    uc = ListDepartmentsUseCase(repo)
    depts = await uc.execute()
    return [DepartmentOut.model_validate(d, from_attributes=True) for d in depts]


@router.get(
    "/{dept_id}",
    response_model=DepartmentOut,
    status_code=status.HTTP_200_OK,
    summary="Obtener departamento por id",
    dependencies=[Depends(require_permission("employees:read"))],
)
async def get_department(
    dept_id: uuid.UUID,
    repo: DepartmentRepository = Depends(_get_dept_repo),
) -> DepartmentOut:
    uc = GetDepartmentUseCase(repo)
    d = await uc.execute(dept_id)
    return DepartmentOut.model_validate(d, from_attributes=True)


@router.post(
    "",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear departamento",
    dependencies=[Depends(require_permission("departments:manage"))],
)
async def create_department(
    body: CreateDepartmentRequest,
    repo: DepartmentRepository = Depends(_get_dept_repo),
) -> DepartmentOut:
    uc = CreateDepartmentUseCase(repo)
    d = await uc.execute(
        CreateDepartmentInput(
            name=body.name,
            description=body.description,
            parent_department_id=body.parent_department_id,
        )
    )
    return DepartmentOut.model_validate(d, from_attributes=True)


@router.patch(
    "/{dept_id}",
    response_model=DepartmentOut,
    status_code=status.HTTP_200_OK,
    summary="Actualizar departamento",
    dependencies=[Depends(require_permission("departments:manage"))],
)
async def update_department(
    dept_id: uuid.UUID,
    body: UpdateDepartmentRequest,
    repo: DepartmentRepository = Depends(_get_dept_repo),
) -> DepartmentOut:
    uc = UpdateDepartmentUseCase(repo)
    d = await uc.execute(
        UpdateDepartmentInput(
            dept_id=dept_id,
            name=body.name,
            description=body.description,
            parent_department_id=body.parent_department_id,
        )
    )
    return DepartmentOut.model_validate(d, from_attributes=True)


@router.delete(
    "/{dept_id}",
    response_model=MessageOut,
    status_code=status.HTTP_200_OK,
    summary="Eliminar departamento",
    dependencies=[Depends(require_permission("departments:manage"))],
)
async def delete_department(
    dept_id: uuid.UUID,
    repo: DepartmentRepository = Depends(_get_dept_repo),
) -> MessageOut:
    uc = DeleteDepartmentUseCase(repo)
    await uc.execute(dept_id)
    return MessageOut(message="Departamento eliminado.", code="dept_deleted")