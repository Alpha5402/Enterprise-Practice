"""Report endpoint tests."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.competitor import Competitor
from app.schemas.analysis_report import AnalysisReportCreate
from app.services.report_service import ReportService


def test_list_and_get_report(db_session: Session) -> None:
    """Report APIs return persisted structured reports."""
    competitor = Competitor(
        name="Acme Cloud",
        industry="Cloud Infrastructure",
        description="Enterprise cloud platform",
        keywords=["pricing"],
        enabled=True,
    )
    db_session.add(competitor)
    db_session.commit()
    db_session.refresh(competitor)

    report = ReportService(db_session).create_report(
        AnalysisReportCreate(
            competitor_id=competitor.id,
            competitor=competitor.name,
            dimension="price",
            risk_level="medium",
            summary="Pricing changes require monitoring.",
            opportunity_points=["Bundle differentiation"],
            threat_points=["Lower entry pricing"],
            confidence_score=0.82,
            source_article_ids=[],
        )
    )

    client = TestClient(app)
    listed = client.get("/api/v1/reports")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == str(report.id)

    fetched = client.get(f"/api/v1/reports/{report.id}")
    assert fetched.status_code == 200
    assert fetched.json()["dimension"] == "price"


def test_get_missing_report_returns_404() -> None:
    """Missing report lookups return 404."""
    client = TestClient(app)
    response = client.get("/api/v1/reports/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404

