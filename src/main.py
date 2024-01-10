import uvicorn
from . import config
from fastapi import FastAPI
from sqlmodel import select
from .database import DatabaseDep, migrate
from .database.player import Player

app = FastAPI()

migrate()


@app.get("/players")
def search_players(db: DatabaseDep) -> list[Player]:
    query = select(Player)
    result = db.exec(query)
    return result.all()


@app.post("/players")
def create_player(player: Player, db: DatabaseDep) -> Player:
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


def main():
    uvicorn.run("src.main:app", host="0.0.0.0", port=config.port, reload=config.debug)
