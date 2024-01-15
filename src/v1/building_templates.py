from http import HTTPStatus

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from ..database import (
    BuildingTemplate,
    DatabaseDep,
)

router = APIRouter(
    prefix="/building-templates",
    tags=["Buildings"],
)


@router.get("")
def search_building_templates(db: DatabaseDep) -> list[BuildingTemplate]:
    query = select(BuildingTemplate).where(BuildingTemplate.not_deleted())
    return db.exec(query).all()


class BlankBuildingTemplate(BaseModel):
    name: str


@router.post("", status_code=HTTPStatus.CREATED)
def create_building_template(
    data: BlankBuildingTemplate, db: DatabaseDep
) -> BuildingTemplate:
    building_template = BuildingTemplate.model_validate(data)
    db.add(building_template)
    db.commit()
    db.refresh(building_template)
    return building_template


@router.get("/{id}")
def get_building_template(id: int, db: DatabaseDep) -> BuildingTemplate:
    query = select(BuildingTemplate).where(
        BuildingTemplate.not_deleted(), BuildingTemplate.id == id
    )
    building_template = db.exec(query).one()
    return building_template


class BuildingTemplatePatch(BaseModel):
    name: str


@router.patch("/{id}")
def patch_building_template(
    id: int, data: BuildingTemplatePatch, db: DatabaseDep
) -> BuildingTemplate:
    query = select(BuildingTemplate).where(
        BuildingTemplate.not_deleted(), BuildingTemplate.id == id
    )
    building_template = db.exec(query).one()
    building_template.name = data.name
    BuildingTemplate.model_validate(building_template)
    db.add(building_template)
    db.commit()
    db.refresh(building_template)
    return building_template


@router.delete("/{id}")
def delete_building_template(id: int, db: DatabaseDep) -> BuildingTemplate:
    query = select(BuildingTemplate).where(
        BuildingTemplate.not_deleted(), BuildingTemplate.id == id
    )
    building_template = db.exec(query).one()
    building_template.delete()
    db.add(building_template)
    db.commit()
    db.refresh(building_template)
    return building_template
