"""Initial schema — Phase 0.

Phase 0 only creates the extension and an empty `app_meta` table so migrations
are wired end-to-end and verifiable. Real entities (users, employees, roles,
permissions, audit_logs, etc.) are introduced in Phases 1–4.

Revertible: down_revision = None.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # uuid-ossp is not required for gen_random_uuid() (pgcrypto / pg16 built-in),
    # but we enable it for symmetry with older tooling and future use.
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "app_meta",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("value", sa.Text, nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        comment="Key/value store for app-level metadata (schema version markers, etc.).",
    )
    op.create_index("ix_app_meta_key", "app_meta", ["key"], unique=True)
    op.bulk_insert(
        sa.table("app_meta", sa.column("key", sa.String), sa.column("value", sa.Text)),
        [{"key": "schema_phase", "value": "0"}, {"key": "schema_marker", "value": "phase0_foundation"}],
    )


def downgrade() -> None:
    op.drop_index("ix_app_meta_key", table_name="app_meta")
    op.drop_table("app_meta")