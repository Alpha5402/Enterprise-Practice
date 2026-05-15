"""Create competitors table."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "202605150001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration."""
    op.create_table(
        "competitors",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("industry", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=False),
        sa.Column("keywords", postgresql.ARRAY(sa.String(length=120)), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_competitors_industry"), "competitors", ["industry"], unique=False)
    op.create_index(op.f("ix_competitors_name"), "competitors", ["name"], unique=False)


def downgrade() -> None:
    """Rollback migration."""
    op.drop_index(op.f("ix_competitors_name"), table_name="competitors")
    op.drop_index(op.f("ix_competitors_industry"), table_name="competitors")
    op.drop_table("competitors")

