"""Competitor endpoint tests."""

from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_db() -> Generator[Session, None, None]:
    """Yield an isolated in-memory database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_list_delete_competitor() -> None:
    """Competitor CRUD endpoints create, list, and delete a resource."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    payload = {
        "name": "Acme Cloud",
        "industry": "Cloud Infrastructure",
        "description": "Enterprise cloud platform",
        "keywords": ["pricing", "release"],
        "enabled": True,
    }

    created = client.post("/api/v1/competitors", json=payload)
    assert created.status_code == 201
    competitor_id = created.json()["id"]

    listed = client.get("/api/v1/competitors")
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == payload["name"]

    deleted = client.delete(f"/api/v1/competitors/{competitor_id}")
    assert deleted.status_code == 204

    app.dependency_overrides.clear()
