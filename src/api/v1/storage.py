from http import HTTPStatus

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from ...database import DatabaseDep, Storage

router = APIRouter(
    prefix="/storage",
    tags=["Players"],
)


@router.get("")
def search_storage(db: DatabaseDep) -> list[Storage]:
    query = select(Storage)
    return db.exec(query).all()


class BlankStorage(BaseModel):
    player_id: int
    material_id: int
    balance: int


@router.post("", status_code=HTTPStatus.CREATED)
def create_material(data: BlankStorage, db: DatabaseDep) -> Storage:
    material = Storage.model_validate(data)
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.get("/{id}")
def get_material(id: int, db: DatabaseDep) -> Storage:
    query = select(Storage).where(Storage.id == id)
    material = db.exec(query).one()
    return material


class StoragePatch(BaseModel):
    player_id: int
    material_id: int
    balance: int


@router.patch("/{id}")
def patch_material(id: int, data: StoragePatch, db: DatabaseDep) -> Storage:
    query = select(Storage).where(Storage.id == id)
    material = db.exec(query).one()
    material.name = data.name
    Storage.model_validate(material)
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.delete("/{id}")
def delete_material(id: int, db: DatabaseDep) -> Storage:
    query = select(Storage).where(Storage.id == id)
    material = db.exec(query).one()
    db.delete(material)
    db.commit()
    return material
