import uvicorn
from . import config
from fastapi import FastAPI
from sqlmodel import Session, select
from .database import engine, initialize
from .database.player import Player

app = FastAPI()

initialize()


@app.get("/players")
def search_players() -> list[Player]:
    with Session(engine) as session:
        query = select(Player)
        result = session.exec(query)
        return result.all()


@app.post("/players")
def create_player(player: Player) -> Player:
    with Session(engine) as session:
        session.add(player)
        session.commit()
        session.refresh(player)
        return player


def main():
    uvicorn.run("src.main:app", host="0.0.0.0", port=config.port, reload=config.debug)
