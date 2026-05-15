"""Collection and article API tests."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.competitor import Competitor
from app.models.news_article import NewsArticle


def create_competitor(db_session: Session) -> Competitor:
    """Create a competitor for collection API tests."""
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
    return competitor


def test_list_articles_filters_by_competitor(db_session: Session) -> None:
    """Article API lists collected articles for a competitor."""
    competitor = create_competitor(db_session)
    article = NewsArticle(
        competitor_id=competitor.id,
        source_type="web",
        source_name="Market News",
        url="https://example.com/acme",
        title="Acme update",
        content="Acme changed pricing.",
        cleaned_content="Acme changed pricing.",
        extra_metadata={},
    )
    db_session.add(article)
    db_session.commit()

    response = TestClient(app).get(f"/api/v1/articles?competitor_id={competitor.id}")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Acme update"


def test_collect_returns_404_for_missing_competitor() -> None:
    """Collection API returns 404 for unknown competitors."""
    response = TestClient(app).post(
        "/api/v1/collect",
        json={
            "competitor_id": "00000000-0000-0000-0000-000000000000",
            "source_url": "https://example.com/feed.xml",
            "crawler": "rss",
        },
    )

    assert response.status_code == 404

