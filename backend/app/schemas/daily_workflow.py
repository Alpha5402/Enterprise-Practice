"""Schemas for daily automation workflow APIs."""

from pydantic import BaseModel, Field


class DailyWorkflowResponse(BaseModel):
    """Response body for a daily collection and analysis run."""

    collected_count: int = Field(ge=0)
    indexed_count: int = Field(ge=0)
    report_count: int = Field(ge=0)
    errors: list[str] = Field(default_factory=list)

