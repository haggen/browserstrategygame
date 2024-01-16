from http import HTTPStatus

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from browserstrategygame.database import DatabaseDep, Material

router = APIRouter(
    prefix="/materials",
    tags=["Materials"],
)


@router.get("")
def search_materials(db: DatabaseDep):
    query = select(Material).where(Material.not_deleted())
    return db.exec(query).all()


class BlankMaterial(BaseModel):
    name: str


@router.post("", status_code=HTTPStatus.CREATED)
def create_material(data: BlankMaterial, db: DatabaseDep):
    material = Material.model_validate(data)
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.get("/{id}")
def get_material(id: int, db: DatabaseDep):
    query = select(Material).where(Material.not_deleted(), Material.id == id)
    material = db.exec(query).one()
    return material


class MaterialPatch(BaseModel):
    name: str


@router.patch("/{id}")
def patch_material(id: int, data: MaterialPatch, db: DatabaseDep):
    query = select(Material).where(Material.not_deleted(), Material.id == id)
    material = db.exec(query).one()
    material.update(material)
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.delete("/{id}")
def delete_material(id: int, db: DatabaseDep):
    query = select(Material).where(Material.not_deleted(), Material.id == id)
    material = db.exec(query).one()
    material.delete()
    db.add(material)
    db.commit()
    db.refresh(material)
    return material