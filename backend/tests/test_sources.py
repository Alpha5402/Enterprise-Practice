"""Source configuration API tests."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.competitor import Competitor


def create_competitor(db_session: Session) -> Competitor:
    """Create a competitor for source API tests."""
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


def test_create_list_delete_source(db_session: Session) -> None:
    """Source APIs create, list, and delete configurations."""
    competitor = create_competitor(db_session)
    client = TestClient(app)

    created = client.post(
        "/api/v1/sources",
        json={
            "competitor_id": str(competitor.id),
            "name": "Acme RSS",
            "source_url": "https://example.com/feed.xml",
            "crawler": "rss",
            "interval_minutes": 1440,
            "enabled": True,
        },
    )
    assert created.status_code == 201
    source_id = created.json()["id"]

    listed = client.get(f"/api/v1/sources?competitor_id={competitor.id}")
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "Acme RSS"

    deleted = client.delete(f"/api/v1/sources/{source_id}")
    assert deleted.status_code == 204

