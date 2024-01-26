from fastapi import APIRouter
from sqlmodel import select, col

from browserstrategygame.database import DatabaseDep, MaterialTransaction

router = APIRouter(
    prefix="/players/{player_id}/transactions",
    tags=["Players"],
)


@router.get("")
def search_transactions(player_id: int, db: DatabaseDep):
    query = (
        select(MaterialTransaction)
        .where(MaterialTransaction.player_id == player_id)
        .order_by(col(MaterialTransaction.created_at))
    )
    return db.exec(query).all()
