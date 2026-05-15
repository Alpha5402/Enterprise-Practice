"""Pydantic schemas for collected news articles."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class NewsArticleCreate(BaseModel):
    """Payload for persisting a collected news article."""

    competitor_id: UUID
    source_type: str = Field(min_length=1, max_length=40)
    source_name: str = Field(min_length=1, max_length=200)
    url: HttpUrl
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)
    cleaned_content: str = Field(min_length=1)
    published_at: datetime | None = None
    extra_metadata: dict[str, str] = Field(default_factory=dict)


class NewsArticleRead(BaseModel):
    """Response body for collected news articles."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    competitor_id: UUID
    source_type: str
    source_name: str
    url: str
    title: str
    content: str
    cleaned_content: str
    published_at: datetime | None
    collected_at: datetime
    extra_metadata: dict[str, str]

