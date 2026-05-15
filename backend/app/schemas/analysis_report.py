"""Pydantic schemas for analysis reports."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

RiskLevel = Literal["low", "medium", "high", "critical"]
AnalysisDimension = Literal["sentiment", "price", "product", "summary"]


class AnalysisReportCreate(BaseModel):
    """Payload for creating a structured analysis report."""

    competitor_id: UUID
    competitor: str = Field(min_length=1, max_length=200)
    dimension: AnalysisDimension
    risk_level: RiskLevel
    summary: str = Field(min_length=1)
    opportunity_points: list[str] = Field(default_factory=list)
    threat_points: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    source_article_ids: list[str] = Field(default_factory=list)


class AnalysisReportRead(AnalysisReportCreate):
    """Response body for structured analysis reports."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime

