"""RAG indexing and retrieval API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.rag.exceptions import RagConfigurationError
from app.schemas.rag import (
    RagIndexArticleRequest,
    RagIndexArticleResponse,
    RagSearchRequest,
    RagSearchResponse,
)
from app.services.rag_service import RagService

router = APIRouter(prefix="/rag")
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/articles/index", response_model=RagIndexArticleResponse)
def index_article(payload: RagIndexArticleRequest, db: DbSession) -> RagIndexArticleResponse:
    """Index one collected article into the RAG vector store."""
    try:
        metadata = RagService(db).index_article(payload.article_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RagConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return RagIndexArticleResponse(
        article_id=payload.article_id,
        chunk_count=len(metadata),
        metadata=metadata,
    )


@router.post("/search", response_model=RagSearchResponse)
def search(payload: RagSearchRequest, db: DbSession) -> RagSearchResponse:
    """Search indexed article chunks by semantic similarity."""
    try:
        results = RagService(db).search(
            query=payload.query,
            competitor_id=payload.competitor_id,
            limit=payload.limit,
        )
    except RagConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return RagSearchResponse(results=results)
