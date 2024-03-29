from http import HTTPStatus

from fastapi import APIRouter, Response
from pydantic import BaseModel
from sqlmodel import select

from browserstrategygame.database import (
    Building,
    BuildingTemplate,
    DatabaseDep,
    Player,
    Storage,
)

router = APIRouter(
    prefix="/buildings",
    tags=["Buildings"],
)


@router.get("")
def search_buildings(db: DatabaseDep):
    query = select(Building).where(Building.not_deleted)
    return db.exec(query).all()


class BlankBuilding(BaseModel):
    building_template_id: int
    player_id: int


@router.post("", status_code=HTTPStatus.CREATED)
def create_building(data: BlankBuilding, db: DatabaseDep):
    building = Building.model_validate(data)
    building_template = db.exec(
        select(BuildingTemplate).where(
            BuildingTemplate.not_deleted,
            BuildingTemplate.id == data.building_template_id,
        )
    ).one()
    player = db.exec(
        select(Player).where(Player.not_deleted, Player.id == data.player_id)
    ).one()
    db.exec(select(Storage).where(Storage.player_id == data.player_id)).all()
    db.add(building)
    for material_cost in building_template.material_costs:
        if not player.pay_stored_material(
            material_cost.material_id, material_cost.quantity
        ):
            db.rollback()
            return Response(status_code=HTTPStatus.UNPROCESSABLE_ENTITY)

    db.commit()
    db.refresh(building)
    return building


@router.get("/{id}")
def get_building(id: int, db: DatabaseDep):
    query = select(Building).where(Building.not_deleted, Building.id == id)
    building = db.exec(query).one()
    return building


@router.delete("/{id}")
def delete_building(id: int, db: DatabaseDep):
    query = select(Building).where(Building.not_deleted, Building.id == id)
    building = db.exec(query).one()
    building.delete()
    db.commit()
    db.refresh(building)
    return building
