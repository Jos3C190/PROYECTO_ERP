"""ORM models: Department, Employee."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPKMixin


class Department(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "departments"
    __table_args__ = ({"comment": "Departments (self-referencing hierarchy)."},)

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    parent_department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        default=None,
    )


class Employee(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "employees"
    __table_args__ = ({"comment": "Employee profiles (optionally linked to a user account)."},)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
        default=None,
    )
    employee_code: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True, index=True
    )
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    document_id: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)
    address: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        default=None,
    )
    position: Mapped[str | None] = mapped_column(String(120), nullable=True, default=None)
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="activo", default="activo"
    )
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)