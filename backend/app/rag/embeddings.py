"""LangChain embedding provider adapters."""

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from langchain_core.embeddings import Embeddings


class ChromaDefaultEmbeddings(Embeddings):
    """Local Chroma default embeddings exposed through LangChain's interface."""

    model = "chroma-default"

    def __init__(self) -> None:
        """Initialize Chroma's built-in embedding function."""
        self.embedding_function = DefaultEmbeddingFunction()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed documents with Chroma's local default embedding model."""
        if not texts:
            return []
        embeddings = self.embedding_function(texts)
        return [list(map(float, embedding)) for embedding in embeddings]

    def embed_query(self, text: str) -> list[float]:
        """Embed one query with Chroma's local default embedding model."""
        return self.embed_documents([text])[0]
