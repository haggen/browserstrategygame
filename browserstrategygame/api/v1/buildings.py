from http import HTTPStatus

from fastapi import APIRouter, Response
from pydantic import BaseModel
from sqlmodel import select

from browserstrategygame.database import (
    Building,
    BuildingTemplate,
    DatabaseDep,
    Player,
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
    db.add(building)
    building_template = db.exec(
        select(BuildingTemplate).where(
            BuildingTemplate.not_deleted,
            BuildingTemplate.id == data.building_template_id,
        )
    ).one()
    db.add(building_template)
    player = db.exec(
        select(Player).where(Player.not_deleted, Player.id == data.player_id)
    ).one()
    db.add(player)
    for material_effect in building_template.material_effects:
        if not player.transact(
            material_id=material_effect.material_id, amount=material_effect.amount
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
