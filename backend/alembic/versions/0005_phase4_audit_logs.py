"""Phase 4 — audit_logs (append-only).

The audit log is insert-only: no UPDATE or DELETE endpoints exist. The
application layer enforces this — the repository exposes only `add` and `list`,
never `update` or `delete`. Each row captures who, what, on which resource,
before/after state (JSONB), IP, user agent, and result.

Keyset pagination over (created_at DESC, id DESC) for efficient cursor-based
paging on large volumes.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=True),
        sa.Column("resource_id", sa.String(64), nullable=True),
        sa.Column("before_state", JSONB, nullable=True),
        sa.Column("after_state", JSONB, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'success'")),
        sa.Column("metadata_", JSONB, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            sa.text("status IN ('success', 'failure')"), name="ck_audit_logs_status"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_audit_logs_user", ondelete="SET NULL"
        ),
        comment="Append-only audit log. No UPDATE/DELETE API surface.",
    )
    # Keyset cursor: (created_at DESC, id DESC) for efficient pagination.
    op.create_index(
        "ix_audit_logs_cursor",
        "audit_logs",
        [sa.text("created_at DESC"), sa.text("id DESC")],
        unique=False,
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)
    op.create_index(
        "ix_audit_logs_resource",
        "audit_logs",
        ["resource_type", "resource_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_resource", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_cursor", table_name="audit_logs")
    op.drop_table("audit_logs")