from fastapi import APIRouter
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


@router.get("/{id}")
def get_material(id: int, db: DatabaseDep):
    query = select(Material).where(Material.not_deleted(), Material.id == id)
    material = db.exec(query).one()
    return material
