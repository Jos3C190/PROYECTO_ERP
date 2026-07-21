"""Phase 3 — departments + employees.

Departments support a self-referencing hierarchy (parent_department_id).
Employees link optionally to a user account and to a department. The status
enum (activo/inactivo/vacaciones/baja) is a CHECK constraint. Photo URL is
stored locally for this boilerplate; the storage interface is abstracted so
S3/MinIO can be plugged later.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

EMPLOYEE_STATUSES = ("activo", "inactivo", "vacaciones", "baja")


def upgrade() -> None:
    # ---------------- departments ----------------
    op.create_table(
        "departments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("parent_department_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("char_length(name) >= 2", name="ck_departments_name_len"),
        sa.UniqueConstraint("name", name="uq_departments_name"),
        sa.ForeignKeyConstraint(
            ["parent_department_id"],
            ["departments.id"],
            name="fk_departments_parent",
            ondelete="SET NULL",
        ),
        comment="Departments (self-referencing hierarchy).",
    )
    op.create_index("ix_departments_name", "departments", ["name"], unique=True)
    op.create_index("ix_departments_parent", "departments", ["parent_department_id"], unique=False)

    # ---------------- employees ----------------
    op.create_table(
        "employees",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("employee_code", sa.String(32), nullable=False),
        sa.Column("first_name", sa.String(120), nullable=False),
        sa.Column("last_name", sa.String(120), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=True),
        sa.Column("birth_date", sa.Date, nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("department_id", UUID(as_uuid=True), nullable=True),
        sa.Column("position", sa.String(120), nullable=True),
        sa.Column("hire_date", sa.Date, nullable=True),
        sa.Column("termination_date", sa.Date, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'activo'")),
        sa.Column("photo_url", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint("char_length(employee_code) >= 2", name="ck_employees_code_len"),
        sa.CheckConstraint("char_length(first_name) >= 2", name="ck_employees_first_name_len"),
        sa.CheckConstraint("char_length(last_name) >= 2", name="ck_employees_last_name_len"),
        sa.CheckConstraint(
            sa.text(f"status IN {EMPLOYEE_STATUSES!r}"),
            name="ck_employees_status",
        ),
        sa.UniqueConstraint("employee_code", name="uq_employees_code"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_employees_user", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            name="fk_employees_department",
            ondelete="SET NULL",
        ),
        comment="Employee profiles (optionally linked to a user account).",
    )
    op.create_index("ix_employees_employee_code", "employees", ["employee_code"], unique=True)
    op.create_index("ix_employees_department_id", "employees", ["department_id"], unique=False)
    op.create_index("ix_employees_user_id", "employees", ["user_id"], unique=True)
    op.create_index("ix_employees_deleted_at", "employees", ["deleted_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_employees_deleted_at", table_name="employees")
    op.drop_index("ix_employees_user_id", table_name="employees")
    op.drop_index("ix_employees_department_id", table_name="employees")
    op.drop_index("ix_employees_employee_code", table_name="employees")
    op.drop_table("employees")
    op.drop_index("ix_departments_parent", table_name="departments")
    op.drop_index("ix_departments_name", table_name="departments")
    op.drop_table("departments")