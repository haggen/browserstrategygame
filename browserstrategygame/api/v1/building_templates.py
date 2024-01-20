from fastapi import APIRouter
from sqlmodel import select

from browserstrategygame.database import (
    BuildingTemplate,
    DatabaseDep,
)

router = APIRouter(
    prefix="/building-templates",
    tags=["Buildings"],
)


@router.get("")
def search_building_templates(db: DatabaseDep):
    query = select(BuildingTemplate).where(BuildingTemplate.not_deleted())
    return db.exec(query).all()
