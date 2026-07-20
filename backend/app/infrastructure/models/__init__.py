"""ORM models package. Importing this module registers all tables on
`Base.metadata`. Phase 0 has no business tables yet (only `app_meta` from the
initial migration); real models arrive in Phases 1–4.

Keep this file as a single import point so `alembic env.py` and tests can do
`from app.infrastructure import models` to ensure full registration.
"""

# Phase 1+ imports will live here, e.g.:
# from app.infrastructure.models.user import User  # noqa: F401
# from app.infrastructure.models.employee import Employee  # noqa: F401
# from app.infrastructure.models.rbac import Role, Permission, RolePermission, UserRole  # noqa: F401
# from app.infrastructure.models.audit import AuditLog  # noqa: F401

__all__: list[str] = []