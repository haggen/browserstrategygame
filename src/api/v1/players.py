from http import HTTPStatus

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from ...database import DatabaseDep, Player, not_deleted

router = APIRouter(
    prefix="/players",
    tags=["Players"],
)


@router.get("/")
def search_players(db: DatabaseDep) -> list[Player]:
    query = select(Player).where(not_deleted(Player))
    return db.exec(query).all()


class BlankPlayer(BaseModel):
    name: str


@router.post("/", status_code=HTTPStatus.CREATED)
def create_player(data: BlankPlayer, db: DatabaseDep) -> Player:
    player = Player.model_validate(data)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@router.get("/{id}")
def get_player(id: int, db: DatabaseDep) -> Player:
    query = select(Player).where(not_deleted(Player), Player.id == id)
    player = db.exec(query).one()
    return player


class PlayerPatch(BaseModel):
    name: str


@router.patch("/{id}")
def patch_player(id: int, data: PlayerPatch, db: DatabaseDep) -> Player:
    query = select(Player).where(not_deleted(Player), Player.id == id)
    player = db.exec(query).one()
    player.name = data.name
    Player.model_validate(player)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@router.delete("/{id}")
def delete_player(id: int, db: DatabaseDep) -> Player:
    query = select(Player).where(not_deleted(Player), Player.id == id)
    player = db.exec(query).one()
    player.delete()
    db.add(player)
    db.commit()
    db.refresh(player)
    return player
