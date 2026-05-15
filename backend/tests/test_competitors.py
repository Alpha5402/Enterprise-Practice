"""Competitor endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app


def test_create_list_delete_competitor() -> None:
    """Competitor CRUD endpoints create, list, and delete a resource."""
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
