from http import HTTPStatus

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from ..database import DatabaseDep, MaterialCost

router = APIRouter(
    prefix="/material-requirements",
    tags=["Buildings"],
)


@router.get("")
def search_material_costs(db: DatabaseDep) -> list[MaterialCost]:
    query = select(MaterialCost).where(MaterialCost.not_deleted())
    return db.exec(query).all()


class BlankRequirement(BaseModel):
    building_template_id: int
    material_id: int
    quantity: int


@router.post("", status_code=HTTPStatus.CREATED)
def create_material_cost(data: BlankRequirement, db: DatabaseDep) -> MaterialCost:
    material_cost = MaterialCost.model_validate(data)
    db.add(material_cost)
    db.commit()
    db.refresh(material_cost)
    return material_cost


@router.get("/{id}")
def get_material_cost(id: int, db: DatabaseDep) -> MaterialCost:
    query = select(MaterialCost).where(
        MaterialCost.not_deleted(), MaterialCost.id == id
    )
    material_cost = db.exec(query).one()
    return material_cost


class RequirementPatch(BaseModel):
    building_template_id: int
    material_id: int
    quantity: int


@router.patch("/{id}")
def patch_material_cost(
    id: int, data: RequirementPatch, db: DatabaseDep
) -> MaterialCost:
    query = select(MaterialCost).where(
        MaterialCost.not_deleted(), MaterialCost.id == id
    )
    material_cost = db.exec(query).one()
    material_cost.name = data.name
    MaterialCost.model_validate(material_cost)
    db.add(material_cost)
    db.commit()
    db.refresh(material_cost)
    return material_cost


@router.delete("/{id}")
def delete_material_cost(id: int, db: DatabaseDep) -> MaterialCost:
    query = select(MaterialCost).where(
        MaterialCost.not_deleted(), MaterialCost.id == id
    )
    material_cost = db.exec(query).one()
    material_cost.delete()
    db.add(material_cost)
    db.commit()
    db.refresh(material_cost)
    return material_cost
