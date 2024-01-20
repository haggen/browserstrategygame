from fastapi import APIRouter
from sqlmodel import select

from browserstrategygame.database import DatabaseDep, MaterialYield

router = APIRouter(
    prefix="/material-yields",
    tags=["Buildings"],
)


@router.get("")
def search_material_yields(db: DatabaseDep):
    query = select(MaterialYield).where(MaterialYield.not_deleted)
    return db.exec(query).all()
