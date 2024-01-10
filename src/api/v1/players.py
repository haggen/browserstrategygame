from fastapi import APIRouter
from sqlmodel import select

from ...database import DatabaseDep
from ...database.player import Player

router = APIRouter(
    prefix="/players",
)


@router.get("/")
def search(db: DatabaseDep) -> list[Player]:
    query = select(Player)
    result = db.exec(query)
    return result.all()


@router.post("/")
def create(player: Player, db: DatabaseDep) -> Player:
    db.add(player)
    db.commit()
    db.refresh(player)
    return player
