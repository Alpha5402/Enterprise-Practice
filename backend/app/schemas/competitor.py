"""Pydantic schemas for competitor APIs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompetitorBase(BaseModel):
    """Shared competitor fields."""

    name: str = Field(min_length=1, max_length=200)
    industry: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    keywords: list[str] = Field(default_factory=list)
    enabled: bool = True


class CompetitorCreate(CompetitorBase):
    """Request body for creating a competitor."""


class CompetitorRead(CompetitorBase):
    """Response body for competitor resources."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime

