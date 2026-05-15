"""Pydantic schemas for RAG APIs."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.embedding_metadata import EmbeddingMetadataRead


class RagIndexArticleRequest(BaseModel):
    """Request body for indexing one article into the vector store."""

    article_id: UUID


class RagIndexArticleResponse(BaseModel):
    """Response body for article indexing."""

    article_id: UUID
    chunk_count: int
    metadata: list[EmbeddingMetadataRead]


class RagSearchRequest(BaseModel):
    """Request body for semantic retrieval."""

    query: str = Field(min_length=1)
    competitor_id: UUID | None = None
    limit: int = Field(default=5, ge=1, le=20)


class RagSearchResult(BaseModel):
    """One retrieval result from the vector store."""

    vector_id: str
    text: str
    metadata: dict[str, str]
    distance: float | None


class RagSearchResponse(BaseModel):
    """Response body for semantic retrieval."""

    results: list[RagSearchResult]

