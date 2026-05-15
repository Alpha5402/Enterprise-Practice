"""Vector store abstractions and Chroma implementation."""

from dataclasses import dataclass
from typing import Protocol

import chromadb

from app.core.config import Settings


@dataclass(frozen=True)
class VectorDocument:
    """A document chunk ready for vector storage."""

    id: str
    text: str
    embedding: list[float]
    metadata: dict[str, str]


@dataclass(frozen=True)
class VectorSearchResult:
    """A vector search result returned by a vector store."""

    id: str
    text: str
    metadata: dict[str, str]
    distance: float | None


class VectorStoreService(Protocol):
    """Protocol for vector store implementations."""

    def add_documents(self, documents: list[VectorDocument]) -> None:
        """Store vectorized documents."""

    def search(
        self,
        query_embedding: list[float],
        limit: int,
        where: dict[str, str] | None = None,
    ) -> list[VectorSearchResult]:
        """Search for semantically similar documents."""

    def delete_by_article(self, article_id: str) -> None:
        """Delete all vectors for an article."""


class ChromaVectorStoreService:
    """Chroma-backed vector store service."""

    def __init__(self, settings: Settings) -> None:
        """Initialize a Chroma HTTP collection from settings."""
        self.client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
        self.collection = self.client.get_or_create_collection(settings.rag_collection_name)

    def add_documents(self, documents: list[VectorDocument]) -> None:
        """Store vectorized documents in Chroma."""
        if not documents:
            return
        self.collection.upsert(
            ids=[document.id for document in documents],
            documents=[document.text for document in documents],
            embeddings=[document.embedding for document in documents],
            metadatas=[document.metadata for document in documents],
        )

    def search(
        self,
        query_embedding: list[float],
        limit: int,
        where: dict[str, str] | None = None,
    ) -> list[VectorSearchResult]:
        """Search Chroma for semantically similar documents."""
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            VectorSearchResult(
                id=str(ids[index]),
                text=str(documents[index]),
                metadata={str(key): str(value) for key, value in (metadatas[index] or {}).items()},
                distance=float(distances[index]) if distances[index] is not None else None,
            )
            for index in range(len(ids))
        ]

    def delete_by_article(self, article_id: str) -> None:
        """Delete all Chroma vectors associated with an article."""
        self.collection.delete(where={"article_id": article_id})

