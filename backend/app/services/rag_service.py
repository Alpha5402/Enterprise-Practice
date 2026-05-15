"""Application service for RAG indexing and retrieval."""

from uuid import UUID

from langchain_core.embeddings import Embeddings
from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.models.embedding_metadata import EmbeddingMetadata
from app.rag.chunking import TextChunker
from app.rag.embeddings import ChromaDefaultEmbeddings
from app.rag.exceptions import RagConfigurationError
from app.rag.vector_store import ChromaVectorStoreService, VectorDocument, VectorStoreService
from app.schemas.embedding_metadata import EmbeddingMetadataCreate
from app.schemas.rag import RagSearchResult
from app.services.article_service import ArticleService
from app.services.embedding_metadata_service import EmbeddingMetadataService


class RagService:
    """Coordinate article indexing and semantic retrieval."""

    def __init__(
        self,
        db: Session,
        app_settings: Settings = settings,
        embedding_provider: Embeddings | None = None,
        vector_store: VectorStoreService | None = None,
        chunker: TextChunker | None = None,
    ) -> None:
        """Initialize RAG dependencies."""
        self.db = db
        self.settings = app_settings
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.chunker = chunker or TextChunker(
            chunk_size=app_settings.rag_chunk_size,
            chunk_overlap=app_settings.rag_chunk_overlap,
        )
        self.article_service = ArticleService(db)
        self.metadata_service = EmbeddingMetadataService(db)

    def index_article(self, article_id: UUID) -> list[EmbeddingMetadata]:
        """Index an article into the configured vector store and return metadata payloads."""
        article = self.article_service.get_article(article_id)
        if article is None:
            raise ValueError(f"Article not found: {article_id}")

        chunks = self.chunker.split(article.cleaned_content)
        vector_store = self._vector_store()
        embedding_provider = self._embedding_provider()
        embeddings = self._embed_documents(embedding_provider, [chunk.text for chunk in chunks])
        if len(embeddings) != len(chunks):
            raise ValueError("Embedding provider returned an unexpected number of vectors")

        vector_store.delete_by_article(str(article.id))
        documents: list[VectorDocument] = []
        metadata_payloads: list[EmbeddingMetadataCreate] = []
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            vector_id = f"article:{article.id}:chunk:{chunk.index}"
            metadata = {
                "article_id": str(article.id),
                "competitor_id": str(article.competitor_id),
                "chunk_index": str(chunk.index),
                "source_type": article.source_type,
                "url": article.url,
                "title": article.title,
            }
            documents.append(
                VectorDocument(
                    id=vector_id,
                    text=chunk.text,
                    embedding=embedding,
                    metadata=metadata,
                )
            )
            metadata_payloads.append(
                EmbeddingMetadataCreate(
                    article_id=article.id,
                    collection_name=self.settings.rag_collection_name,
                    vector_id=vector_id,
                    chunk_index=chunk.index,
                    chunk_text=chunk.text,
                    embedding_model=self.settings.embedding_model,
                    extra_metadata={
                        "start_offset": str(chunk.start_offset),
                        "end_offset": str(chunk.end_offset),
                    },
                )
            )

        vector_store.add_documents(documents)
        return self.metadata_service.replace_for_article(article.id, metadata_payloads)

    def index_competitor_articles(self, competitor_id: UUID) -> list[EmbeddingMetadata]:
        """Index all collected articles for a competitor."""
        indexed: list[EmbeddingMetadata] = []
        for article in self.article_service.list_articles(competitor_id=competitor_id):
            indexed.extend(self.index_article(article.id))
        return indexed

    def search(
        self,
        query: str,
        competitor_id: UUID | None = None,
        limit: int = 5,
    ) -> list[RagSearchResult]:
        """Retrieve semantically relevant chunks from the vector store."""
        where = {"competitor_id": str(competitor_id)} if competitor_id is not None else None
        query_embedding = self._embed_query(query)
        results = self._vector_store().search(
            query_embedding=query_embedding,
            limit=limit,
            where=where,
        )
        return [
            RagSearchResult(
                vector_id=result.id,
                text=result.text,
                metadata=result.metadata,
                distance=result.distance,
            )
            for result in results
        ]

    def _embedding_provider(self) -> Embeddings:
        """Return the configured embedding provider."""
        if self.embedding_provider is None:
            self.embedding_provider = ChromaDefaultEmbeddings()
        return self.embedding_provider

    def _vector_store(self) -> VectorStoreService:
        """Return the configured vector store."""
        if self.vector_store is None:
            try:
                self.vector_store = ChromaVectorStoreService(self.settings)
            except Exception as exc:
                raise RagConfigurationError("Vector store is unavailable") from exc
        return self.vector_store

    def _embed_documents(
        self,
        embedding_provider: Embeddings,
        texts: list[str],
    ) -> list[list[float]]:
        """Embed documents and normalize provider failures."""
        try:
            return embedding_provider.embed_documents(texts)
        except Exception as exc:
            raise RagConfigurationError("Embedding provider is unavailable") from exc

    def _embed_query(self, query: str) -> list[float]:
        """Embed a query and normalize provider failures."""
        try:
            return self._embedding_provider().embed_query(query)
        except Exception as exc:
            raise RagConfigurationError("Embedding provider is unavailable") from exc
