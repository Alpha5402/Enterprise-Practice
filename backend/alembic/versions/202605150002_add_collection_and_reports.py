"""Add collection articles, analysis reports, and embedding metadata."""

import sqlalchemy as sa

from alembic import op

revision = "202605150002"
down_revision = "202605150001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration."""
    op.create_table(
        "news_articles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("competitor_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("source_name", sa.String(length=200), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("cleaned_content", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("extra_metadata", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_index(op.f("ix_news_articles_competitor_id"), "news_articles", ["competitor_id"])
    op.create_index(op.f("ix_news_articles_source_type"), "news_articles", ["source_type"])
    op.create_index(op.f("ix_news_articles_url"), "news_articles", ["url"])

    op.create_table(
        "analysis_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("competitor_id", sa.Uuid(), nullable=False),
        sa.Column("competitor", sa.String(length=200), nullable=False),
        sa.Column("dimension", sa.String(length=80), nullable=False),
        sa.Column("risk_level", sa.String(length=40), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("opportunity_points", sa.JSON(), nullable=False),
        sa.Column("threat_points", sa.JSON(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("source_article_ids", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analysis_reports_competitor"), "analysis_reports", ["competitor"])
    op.create_index(
        op.f("ix_analysis_reports_competitor_id"),
        "analysis_reports",
        ["competitor_id"],
    )
    op.create_index(op.f("ix_analysis_reports_dimension"), "analysis_reports", ["dimension"])
    op.create_index(op.f("ix_analysis_reports_risk_level"), "analysis_reports", ["risk_level"])

    op.create_table(
        "embeddings_metadata",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("article_id", sa.Uuid(), nullable=False),
        sa.Column("collection_name", sa.String(length=120), nullable=False),
        sa.Column("vector_id", sa.String(length=200), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding_model", sa.String(length=120), nullable=False),
        sa.Column("extra_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["news_articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vector_id"),
    )
    op.create_index(
        op.f("ix_embeddings_metadata_article_id"),
        "embeddings_metadata",
        ["article_id"],
    )
    op.create_index(
        op.f("ix_embeddings_metadata_collection_name"),
        "embeddings_metadata",
        ["collection_name"],
    )
    op.create_index(op.f("ix_embeddings_metadata_vector_id"), "embeddings_metadata", ["vector_id"])


def downgrade() -> None:
    """Rollback migration."""
    op.drop_index(op.f("ix_embeddings_metadata_vector_id"), table_name="embeddings_metadata")
    op.drop_index(op.f("ix_embeddings_metadata_collection_name"), table_name="embeddings_metadata")
    op.drop_index(op.f("ix_embeddings_metadata_article_id"), table_name="embeddings_metadata")
    op.drop_table("embeddings_metadata")

    op.drop_index(op.f("ix_analysis_reports_risk_level"), table_name="analysis_reports")
    op.drop_index(op.f("ix_analysis_reports_dimension"), table_name="analysis_reports")
    op.drop_index(op.f("ix_analysis_reports_competitor_id"), table_name="analysis_reports")
    op.drop_index(op.f("ix_analysis_reports_competitor"), table_name="analysis_reports")
    op.drop_table("analysis_reports")

    op.drop_index(op.f("ix_news_articles_url"), table_name="news_articles")
    op.drop_index(op.f("ix_news_articles_source_type"), table_name="news_articles")
    op.drop_index(op.f("ix_news_articles_competitor_id"), table_name="news_articles")
    op.drop_table("news_articles")
