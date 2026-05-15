"""Pydantic schemas for collection APIs."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.news_article import NewsArticleRead

CrawlerKind = Literal["rss", "web"]


class CollectRequest(BaseModel):
    """Request body for collecting articles from a public source."""

    competitor_id: UUID
    source_url: HttpUrl
    crawler: CrawlerKind


class CollectResponse(BaseModel):
    """Response body for article collection."""

    collected_count: int
    articles: list[NewsArticleRead]


class IndexCompetitorResponse(BaseModel):
    """Response body for indexing all articles for a competitor."""

    competitor_id: UUID
    metadata_count: int = Field(ge=0)

