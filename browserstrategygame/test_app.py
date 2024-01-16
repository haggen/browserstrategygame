from fastapi.testclient import TestClient
from sqlmodel import Session

from . import app, database

client = TestClient(app.app)


def test_database():
    with Session(database.engine) as db:
        material = db.get(database.Material, 1)
        assert material.id, "Database haven't been seeded"


def test_materials():
    resp = client.get("/v1/materials")
    assert resp.status_code == 200
    assert any(material["id"] == 1 for material in resp.json())
