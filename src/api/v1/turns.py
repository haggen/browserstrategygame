from fastapi import APIRouter
from sqlmodel import select
from datetime import datetime, timedelta

from ...database import DatabaseDep
from ...database.turn import Turn

router = APIRouter(
    prefix="/turns",
)


@router.get("/")
def search(db: DatabaseDep) -> list[Turn]:
    query = select(Turn)
    result = db.exec(query)
    return result.all()


@router.post("/")
def create(turn: Turn, db: DatabaseDep) -> Turn:
    turn.started_at = datetime.utcnow()
    turn.ends_at = turn.started_at + timedelta(minutes=1)
    db.add(turn)
    db.commit()
    db.refresh(turn)
    return turn
