"""Analysis report API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analysis_report import AnalysisReportRead
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports")
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[AnalysisReportRead])
def list_reports(
    db: DbSession,
    competitor_id: Annotated[UUID | None, Query()] = None,
) -> list[AnalysisReportRead]:
    """List structured analysis reports."""
    return ReportService(db).list_reports(competitor_id=competitor_id)


@router.get("/{report_id}", response_model=AnalysisReportRead)
def get_report(report_id: UUID, db: DbSession) -> AnalysisReportRead:
    """Return one structured analysis report."""
    report = ReportService(db).get_report(report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report

