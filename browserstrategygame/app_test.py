from datetime import UTC, datetime

from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from browserstrategygame.app import app
from browserstrategygame.database import (
    yield_session,
    Material,
    Player,
    Realm,
    Storage,
    BuildingTemplate,
    MaterialCost,
)

# I still don't quite understand why StaticPool is needed here.
# Without it, it seems that each connection instances its own database.
# I get "table doesn't exit" errors during the endpoint, even though tables were created here in the test script.
engine = create_engine(
    "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
)
client = TestClient(app)


def override_yield_session():
    """
    Use test database.
    """

    with Session(engine) as session:
        yield session


app.dependency_overrides[yield_session] = override_yield_session


@fixture(autouse=True)
def db():
    """
    Recreate database and yield session for every test case.
    """

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)

def test_search_realms(db):
    realm = Realm(name="Realm")
    db.add(realm)
    db.commit()
    db.refresh(realm)
    response = client.get("/v1/realms")
    assert response.status_code == 200
    assert any(server["name"] == realm.name for server in response.json())


def test_get_realm(db):
    realm = Realm(name="Realm")
    db.add(realm)
    db.commit()
    db.refresh(realm)
    response = client.get(f"/v1/realms/{realm.id}")
    assert response.status_code == 200
    assert response.json() == realm.model_dump(mode="json")


def test_search_materials(db):
    stone = Material(name="Stone")
    db.add(stone)

    wood = Material(name="Wood", deleted_at=datetime.now(UTC))
    db.add(wood)

    db.commit()
    db.refresh(stone)
    db.refresh(wood)

    response = client.get("/v1/materials")

    assert response.status_code == 200
    assert any(material["name"] == stone.name for material in response.json())
    assert not all(material["name"] == wood.name for material in response.json())


def test_get_material(db):
    stone = Material(name="Stone")
    db.add(stone)

    wood = Material(name="Wood", deleted_at=datetime.now(UTC))
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
    wood = Material(name="Wood")
    db.add(wood)
    db.commit()
    db.refresh(wood)

    player = Player(
        name="Player",
        realm=Realm(name="Realm"),
        storage=[Storage(material_id=wood.id, balance=100)],
    )
    db.add(player)
    db.commit()
    db.refresh(player)

    building_template = BuildingTemplate(
        name="Quarry",
        realm_id=player.realm.id,
        material_costs=[MaterialCost(material_id=wood.id, quantity=75)],
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
