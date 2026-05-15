"""Pydantic schemas for analysis workflow APIs and structured output."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.analysis_report import AnalysisDimension, AnalysisReportRead, RiskLevel


class StructuredAnalysisOutput(BaseModel):
    """Strict JSON output produced by each analysis agent."""

    competitor: str = Field(min_length=1, max_length=200)
    dimension: AnalysisDimension
    risk_level: RiskLevel
    summary: str = Field(min_length=1)
    opportunity_points: list[str] = Field(default_factory=list)
    threat_points: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)


class AnalyzeRequest(BaseModel):
    """Request body for competitive analysis."""

    competitor_id: UUID
    query: str = Field(default="latest competitive signals", min_length=1)
    context_limit: int = Field(default=5, ge=1, le=20)


class AnalyzeResponse(BaseModel):
    """Response body for completed competitive analysis."""

    reports: list[AnalysisReportRead]

