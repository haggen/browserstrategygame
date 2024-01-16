from http import HTTPStatus

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from browserstrategygame.database import DatabaseDep, Player

router = APIRouter(
    prefix="/players",
    tags=["Players"],
)


@router.get("")
def search_players(db: DatabaseDep):
    query = select(Player).where(Player.not_deleted())
    return db.exec(query).all()


class BlankPlayer(BaseModel):
    name: str


@router.post("", status_code=HTTPStatus.CREATED)
def create_player(data: BlankPlayer, db: DatabaseDep):
    player = Player.model_validate(data)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@router.get("/{id}")
def get_player(id: int, db: DatabaseDep):
    query = select(Player).where(Player.not_deleted(), Player.id == id)
    player = db.exec(query).one()
    return player


class PlayerPatch(BaseModel):
    name: str


@router.patch("/{id}")
def patch_player(id: int, data: PlayerPatch, db: DatabaseDep):
    query = select(Player).where(Player.not_deleted(), Player.id == id)
    player = db.exec(query).one()
    player.update(player)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@router.delete("/{id}")
def delete_player(id: int, db: DatabaseDep):
    query = select(Player).where(Player.not_deleted(), Player.id == id)
    player = db.exec(query).one()
    player.delete()
    db.add(player)
    db.commit()
    db.refresh(player)
    return player
