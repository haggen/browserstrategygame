from fastapi import APIRouter
from sqlmodel import select

from browserstrategygame.database import DatabaseDep, MaterialEffect

router = APIRouter(
    prefix="/material-effects",
    tags=["Buildings"],
)


@router.get("")
def search_material_effects(db: DatabaseDep):
    query = select(MaterialEffect).where(MaterialEffect.not_deleted)
    return db.exec(query).all()
