"""Automation workflow API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.daily_workflow import DailyWorkflowResponse
from app.services.daily_workflow_service import DailyWorkflowService

router = APIRouter(prefix="/automation")
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/daily-run", response_model=DailyWorkflowResponse)
def run_daily_workflow(
    db: DbSession,
    competitor_id: Annotated[UUID | None, Query()] = None,
) -> DailyWorkflowResponse:
    """Run saved-source collection, indexing, and analysis once."""
    return DailyWorkflowService(db).run(competitor_id=competitor_id)

