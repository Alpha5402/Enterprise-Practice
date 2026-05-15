"""Daily workflow API tests."""

from fastapi.testclient import TestClient

from app.main import app


def test_daily_workflow_without_sources_returns_empty_summary() -> None:
    """Daily workflow returns an empty summary when no sources are configured."""
    response = TestClient(app).post("/api/v1/automation/daily-run")

    assert response.status_code == 200
    assert response.json()["collected_count"] == 0
    assert response.json()["indexed_count"] == 0
    assert response.json()["report_count"] == 0

