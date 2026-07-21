"""ORM models package. Importing this module registers all tables on
`Base.metadata`. Keep this file as a single import point so `alembic env.py`
and tests can do `from app.infrastructure import models` to ensure full
registration.
"""

from app.infrastructure.models.auth import PasswordResetToken, RefreshToken  # noqa: F401
from app.infrastructure.models.employee import Department, Employee  # noqa: F401
from app.infrastructure.models.rbac import (  # noqa: F401
    Permission,
    Role,
    RolePermission,
    UserRole,
)
from app.infrastructure.models.user import User  # noqa: F401

__all__: list[str] = [
    "User",
    "RefreshToken",
    "PasswordResetToken",
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "Department",
    "Employee",
]