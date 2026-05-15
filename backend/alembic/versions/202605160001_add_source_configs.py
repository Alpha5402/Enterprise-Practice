"""Add source configurations."""

import sqlalchemy as sa

from alembic import op

revision = "202605160001"
down_revision = "202605150002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration."""
    op.create_table(
        "source_configs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("competitor_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=False),
        sa.Column("crawler", sa.String(length=20), nullable=False),
        sa.Column("interval_minutes", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_source_configs_competitor_id"), "source_configs", ["competitor_id"])


def downgrade() -> None:
    """Rollback migration."""
    op.drop_index(op.f("ix_source_configs_competitor_id"), table_name="source_configs")
    op.drop_table("source_configs")

