"""Collection and indexing API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crawlers.rss.rss_crawler import RssCrawler
from app.crawlers.web.web_crawler import WebCrawler
from app.db.session import get_db
from app.rag.exceptions import RagConfigurationError
from app.schemas.collection import CollectRequest, CollectResponse, IndexCompetitorResponse
from app.services.collection_service import CollectionService
from app.services.competitor_service import CompetitorService
from app.services.rag_service import RagService

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/collect", response_model=CollectResponse)
def collect(payload: CollectRequest, db: DbSession) -> CollectResponse:
    """Collect public articles for a competitor."""
    competitor = CompetitorService(db).get_competitor(payload.competitor_id)
    if competitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found")

    crawler = RssCrawler() if payload.crawler == "rss" else WebCrawler()
    try:
        articles = CollectionService(db).collect_for_competitor(
            competitor_id=payload.competitor_id,
            source_url=str(payload.source_url),
            crawler=crawler,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Collection failed: {exc}",
        ) from exc

    return CollectResponse(collected_count=len(articles), articles=articles)


@router.post("/competitors/{competitor_id}/index", response_model=IndexCompetitorResponse)
def index_competitor_articles(competitor_id: UUID, db: DbSession) -> IndexCompetitorResponse:
    """Index all collected articles for a competitor into the vector store."""
    competitor = CompetitorService(db).get_competitor(competitor_id)
    if competitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found")

    try:
        metadata = RagService(db).index_competitor_articles(competitor_id)
    except RagConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return IndexCompetitorResponse(competitor_id=competitor_id, metadata_count=len(metadata))

