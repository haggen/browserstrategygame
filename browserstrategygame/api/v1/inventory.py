from fastapi import APIRouter
from sqlmodel import select

from browserstrategygame.database import DatabaseDep, MaterialBalance

router = APIRouter(
    prefix="/players/{player_id}/inventory",
    tags=["Players"],
)


@router.get("")
def get_inventory(player_id: int, db: DatabaseDep):
    query = select(MaterialBalance).where(MaterialBalance.player_id == player_id)
    return db.exec(query).all()
