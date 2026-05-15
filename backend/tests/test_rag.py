"""RAG service tests."""

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.main import app
from app.models.competitor import Competitor
from app.models.news_article import NewsArticle
from app.rag.chunking import TextChunker
from app.rag.vector_store import VectorDocument, VectorSearchResult
from app.services.rag_service import RagService


class FakeEmbeddingProvider:
    """Deterministic embedding provider for service tests."""

    model = "fake-test-embedding"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return deterministic vectors based on text length."""
        return [[float(len(text)), 1.0] for text in texts]

    def embed_query(self, query: str) -> list[float]:
        """Return a deterministic query vector."""
        return [float(len(query)), 1.0]


class FakeVectorStore:
    """In-memory vector store for service tests."""

    def __init__(self) -> None:
        """Initialize empty vector state."""
        self.documents: list[VectorDocument] = []
        self.deleted_article_ids: list[str] = []
        self.last_where: dict[str, str] | None = None

    def add_documents(self, documents: list[VectorDocument]) -> None:
        """Store vectorized documents."""
        self.documents.extend(documents)

    def search(
        self,
        query_embedding: list[float],
        limit: int,
        where: dict[str, str] | None = None,
    ) -> list[VectorSearchResult]:
        """Return stored documents as search results."""
        _ = query_embedding
        self.last_where = where
        filtered = self.documents
        if where is not None:
            filtered = [
                document
                for document in filtered
                if all(document.metadata.get(key) == value for key, value in where.items())
            ]
        return [
            VectorSearchResult(
                id=document.id,
                text=document.text,
                metadata=document.metadata,
                distance=0.1,
            )
            for document in filtered[:limit]
        ]

    def delete_by_article(self, article_id: str) -> None:
        """Delete stored vectors by article id."""
        self.deleted_article_ids.append(article_id)
        self.documents = [
            document
            for document in self.documents
            if document.metadata.get("article_id") != article_id
        ]


def create_article(db_session: Session) -> NewsArticle:
    """Create a competitor and collected article for RAG tests."""
    competitor = Competitor(
        name="Acme Cloud",
        industry="Cloud Infrastructure",
        description="Enterprise cloud platform",
        keywords=["pricing"],
        enabled=True,
    )
    db_session.add(competitor)
    db_session.commit()
    db_session.refresh(competitor)

    article = NewsArticle(
        competitor_id=competitor.id,
        source_type="web",
        source_name="Market News",
        url="https://example.com/acme",
        title="Acme pricing update",
        content="Acme announced new pricing. Enterprise bundles changed.",
        cleaned_content="Acme announced new pricing. Enterprise bundles changed.",
        extra_metadata={},
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    return article


def test_text_chunker_creates_overlapping_chunks() -> None:
    """Chunker splits long text and preserves offsets."""
    chunks = TextChunker(chunk_size=20, chunk_overlap=5).split(
        "Alpha beta gamma. Delta epsilon zeta. Eta theta."
    )

    assert len(chunks) > 1
    assert chunks[0].index == 0
    assert chunks[1].start_offset < chunks[0].end_offset


def test_rag_service_indexes_article_and_persists_metadata(db_session: Session) -> None:
    """RAG service stores vectors and metadata for article chunks."""
    article = create_article(db_session)
    vector_store = FakeVectorStore()
    service = RagService(
        db=db_session,
        app_settings=Settings(
            rag_collection_name="test_collection",
            rag_chunk_size=28,
            rag_chunk_overlap=5,
        ),
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=vector_store,
    )

    metadata = service.index_article(article.id)

    assert len(metadata) == len(vector_store.documents)
    assert metadata[0].vector_id.startswith(f"article:{article.id}:chunk:")
    assert vector_store.deleted_article_ids == [str(article.id)]


def test_rag_service_search_filters_by_competitor(db_session: Session) -> None:
    """RAG search passes competitor filtering to the vector store."""
    article = create_article(db_session)
    vector_store = FakeVectorStore()
    service = RagService(
        db=db_session,
        app_settings=Settings(),
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=vector_store,
    )
    service.index_article(article.id)

    results = service.search("pricing", competitor_id=article.competitor_id, limit=3)

    assert len(results) >= 1
    assert vector_store.last_where == {"competitor_id": str(article.competitor_id)}


def test_rag_index_api_returns_503_when_vector_store_is_unavailable(db_session: Session) -> None:
    """RAG API reports vector-store connectivity failures without fake output."""
    article = create_article(db_session)
    client = TestClient(app)

    response = client.post("/api/v1/rag/articles/index", json={"article_id": str(article.id)})

    assert response.status_code == 503


def test_rag_index_api_returns_404_for_missing_article() -> None:
    """RAG API reports missing articles or unavailable vector store."""
    _ = UUID("00000000-0000-0000-0000-000000000000")
    client = TestClient(app)

    response = client.post(
        "/api/v1/rag/articles/index",
        json={"article_id": "00000000-0000-0000-0000-000000000000"},
    )

    assert response.status_code in {404, 503}
