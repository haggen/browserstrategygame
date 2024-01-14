from http import HTTPStatus

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from ...database import DatabaseDep, MaterialRequirement

router = APIRouter(
    prefix="/material-requirements",
    tags=["Buildings"],
)


@router.get("")
def search_material_requirements(db: DatabaseDep) -> list[MaterialRequirement]:
    query = select(MaterialRequirement).where(MaterialRequirement.not_deleted())
    return db.exec(query).all()


class BlankRequirement(BaseModel):
    building_template_id: int
    material_id: int
    quantity: int


@router.post("", status_code=HTTPStatus.CREATED)
def create_material_requirement(
    data: BlankRequirement, db: DatabaseDep
) -> MaterialRequirement:
    material_requirement = MaterialRequirement.model_validate(data)
    db.add(material_requirement)
    db.commit()
    db.refresh(material_requirement)
    return material_requirement


@router.get("/{id}")
def get_material_requirement(id: int, db: DatabaseDep) -> MaterialRequirement:
    query = select(MaterialRequirement).where(
        MaterialRequirement.not_deleted(), MaterialRequirement.id == id
    )
    material_requirement = db.exec(query).one()
    return material_requirement


class RequirementPatch(BaseModel):
    building_template_id: int
    material_id: int
    quantity: int


@router.patch("/{id}")
def patch_material_requirement(
    id: int, data: RequirementPatch, db: DatabaseDep
) -> MaterialRequirement:
    query = select(MaterialRequirement).where(
        MaterialRequirement.not_deleted(), MaterialRequirement.id == id
    )
    material_requirement = db.exec(query).one()
    material_requirement.name = data.name
    MaterialRequirement.model_validate(material_requirement)
    db.add(material_requirement)
    db.commit()
    db.refresh(material_requirement)
    return material_requirement


@router.delete("/{id}")
def delete_material_requirement(id: int, db: DatabaseDep) -> MaterialRequirement:
    query = select(MaterialRequirement).where(
        MaterialRequirement.not_deleted(), MaterialRequirement.id == id
    )
    material_requirement = db.exec(query).one()
    material_requirement.delete()
    db.add(material_requirement)
    db.commit()
    db.refresh(material_requirement)
    return material_requirement
