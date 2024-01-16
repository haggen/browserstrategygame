from fastapi import APIRouter
from sqlmodel import select

from browserstrategygame.database import DatabaseDep, MaterialCost

router = APIRouter(
    prefix="/material-costs",
    tags=["Buildings"],
)


@router.get("")
def search_material_costs(db: DatabaseDep):
    query = select(MaterialCost).where(MaterialCost.not_deleted())
    return db.exec(query).all()
