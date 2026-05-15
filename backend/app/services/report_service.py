"""Business operations for analysis reports."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis_report import AnalysisReport
from app.schemas.analysis_report import AnalysisReportCreate


class ReportService:
    """Coordinate persistence operations for analysis reports."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.db = db

    def list_reports(self, competitor_id: UUID | None = None) -> list[AnalysisReport]:
        """Return analysis reports, optionally scoped to a competitor."""
        statement = select(AnalysisReport).order_by(AnalysisReport.created_at.desc())
        if competitor_id is not None:
            statement = statement.where(AnalysisReport.competitor_id == competitor_id)
        return list(self.db.scalars(statement).all())

    def get_report(self, report_id: UUID) -> AnalysisReport | None:
        """Return a report by id."""
        return self.db.get(AnalysisReport, report_id)

    def create_report(self, payload: AnalysisReportCreate) -> AnalysisReport:
        """Create and persist an analysis report."""
        report = AnalysisReport(**payload.model_dump())
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

