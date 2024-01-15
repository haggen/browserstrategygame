from fastapi import APIRouter
from sqlmodel import select

from ..database import DatabaseDep, Storage

router = APIRouter(
    prefix="/players/{player_id}/storage",
    tags=["Players"],
)


@router.get("")
def search_storage(player_id: int, db: DatabaseDep) -> list[Storage]:
    query = select(Storage).where(Storage.player_id == player_id)
    return db.exec(query).all()
