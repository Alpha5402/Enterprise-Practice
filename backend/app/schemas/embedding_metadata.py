"""Pydantic schemas for vector-store metadata."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EmbeddingMetadataCreate(BaseModel):
    """Payload for storing metadata about a vectorized chunk."""

    article_id: UUID
    collection_name: str = Field(min_length=1, max_length=120)
    vector_id: str = Field(min_length=1, max_length=200)
    chunk_index: int = Field(ge=0)
    chunk_text: str = Field(min_length=1)
    embedding_model: str = Field(min_length=1, max_length=120)
    extra_metadata: dict[str, str] = Field(default_factory=dict)


class EmbeddingMetadataRead(EmbeddingMetadataCreate):
    """Response body for vector-store metadata records."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime

