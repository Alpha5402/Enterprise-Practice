"""Business operations for embedding metadata records."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.embedding_metadata import EmbeddingMetadata
from app.schemas.embedding_metadata import EmbeddingMetadataCreate


class EmbeddingMetadataService:
    """Coordinate persistence operations for embedding metadata."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.db = db

    def list_by_article(self, article_id: UUID) -> list[EmbeddingMetadata]:
        """Return vector metadata records for an article."""
        statement = (
            select(EmbeddingMetadata)
            .where(EmbeddingMetadata.article_id == article_id)
            .order_by(EmbeddingMetadata.chunk_index.asc())
        )
        return list(self.db.scalars(statement).all())

    def create_metadata(self, payload: EmbeddingMetadataCreate) -> EmbeddingMetadata:
        """Create and persist an embedding metadata record."""
        metadata = EmbeddingMetadata(**payload.model_dump())
        self.db.add(metadata)
        self.db.commit()
        self.db.refresh(metadata)
        return metadata

    def replace_for_article(
        self,
        article_id: UUID,
        payloads: list[EmbeddingMetadataCreate],
    ) -> list[EmbeddingMetadata]:
        """Replace all vector metadata records for an article."""
        existing = self.list_by_article(article_id)
        for metadata in existing:
            self.db.delete(metadata)
        records = [EmbeddingMetadata(**payload.model_dump()) for payload in payloads]
        self.db.add_all(records)
        self.db.commit()
        for record in records:
            self.db.refresh(record)
        return records

