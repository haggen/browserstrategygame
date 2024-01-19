from datetime import UTC, datetime

from fastapi.testclient import TestClient
from pytest import fixture
from sqlmodel import Session

from . import app, database

client = TestClient(app.app)

database.connect("sqlite:///test.db")


@fixture(autouse=True)
def db():
    """
    Recreate database and yield session for every test case.
    """

    database.migrate()

    with Session(database.engine) as session:
        yield session

    database.drop()


def test_search_materials(db):
    stone = database.Material(name="Stone")
    db.add(stone)

    wood = database.Material(name="Wood", deleted_at=datetime.now(UTC))
    db.add(wood)

    db.commit()
    db.refresh(stone)
    db.refresh(wood)

    response = client.get("/v1/materials")

    assert response.status_code == 200
    assert any(material["name"] == stone.name for material in response.json())
    assert not all(material["name"] == wood.name for material in response.json())


def test_get_material(db):
    stone = database.Material(name="Stone")
    db.add(stone)

    wood = database.Material(name="Wood", deleted_at=datetime.now(UTC))
    db.add(wood)

    db.commit()
    db.refresh(stone)
    db.refresh(wood)

    response = client.get(f"/v1/materials/{stone.id}")
    assert response.status_code == 200
    assert response.json() == stone.model_dump(mode="json")

    response = client.get(f"/v1/materials/{wood.id}")
    assert response.status_code == 404


def test_create_building(db):
    wood = database.Material(name="Wood")
    db.add(wood)
    db.commit()
    db.refresh(wood)

    player = database.Player(
        name="Player",
        realm=database.Realm(name="Realm"),
        storage=[database.Storage(material_id=wood.id, balance=100)],
    )
    db.add(player)
    db.commit()
    db.refresh(player)

    building_template = database.BuildingTemplate(
        name="Quarry",
        material_costs=[database.MaterialCost(material_id=wood.id, quantity=75)],
    )
    db.add(building_template)
    db.commit()
    db.refresh(building_template)

    response = client.post(
        "/v1/buildings",
        json={
            "player_id": player.id,
            "building_template_id": building_template.id,
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/v1/buildings",
        json={
            "player_id": player.id,
            "building_template_id": building_template.id,
        },
    )

    assert response.status_code == 422
