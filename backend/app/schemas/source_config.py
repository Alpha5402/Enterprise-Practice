"""Pydantic schemas for persistent source configurations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.schemas.collection import CrawlerKind


class SourceConfigCreate(BaseModel):
    """Request body for creating a source configuration."""

    competitor_id: UUID
    name: str = Field(min_length=1, max_length=200)
    source_url: HttpUrl
    crawler: CrawlerKind
    interval_minutes: int = Field(default=1440, ge=5)
    enabled: bool = True


class SourceConfigRead(BaseModel):
    """Response body for source configurations."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    competitor_id: UUID
    name: str
    source_url: str
    crawler: CrawlerKind
    interval_minutes: int
    enabled: bool
    created_at: datetime
    updated_at: datetime

