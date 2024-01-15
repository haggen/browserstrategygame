from http import HTTPStatus

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from ..database import DatabaseDep, MaterialYield

router = APIRouter(
    prefix="/material-yields",
    tags=["Buildings"],
)


@router.get("")
def search_material_yields(db: DatabaseDep) -> list[MaterialYield]:
    query = select(MaterialYield).where(MaterialYield.not_deleted())
    return db.exec(query).all()


class BlankRequirement(BaseModel):
    building_template_id: int
    material_id: int
    quantity: int


@router.post("", status_code=HTTPStatus.CREATED)
def create_material_yield(data: BlankRequirement, db: DatabaseDep) -> MaterialYield:
    material_yield = MaterialYield.model_validate(data)
    db.add(material_yield)
    db.commit()
    db.refresh(material_yield)
    return material_yield


@router.get("/{id}")
def get_material_yield(id: int, db: DatabaseDep) -> MaterialYield:
    query = select(MaterialYield).where(
        MaterialYield.not_deleted(), MaterialYield.id == id
    )
    material_yield = db.exec(query).one()
    return material_yield


class RequirementPatch(BaseModel):
    building_template_id: int
    material_id: int
    quantity: int


@router.patch("/{id}")
def patch_material_yield(
    id: int, data: RequirementPatch, db: DatabaseDep
) -> MaterialYield:
    query = select(MaterialYield).where(
        MaterialYield.not_deleted(), MaterialYield.id == id
    )
    material_yield = db.exec(query).one()
    material_yield.name = data.name
    MaterialYield.model_validate(material_yield)
    db.add(material_yield)
    db.commit()
    db.refresh(material_yield)
    return material_yield


@router.delete("/{id}")
def delete_material_yield(id: int, db: DatabaseDep) -> MaterialYield:
    query = select(MaterialYield).where(
        MaterialYield.not_deleted(), MaterialYield.id == id
    )
    material_yield = db.exec(query).one()
    material_yield.delete()
    db.add(material_yield)
    db.commit()
    db.refresh(material_yield)
    return material_yield
