import uvicorn

from fastapi import FastAPI

from . import config
from .api import v1
from .database import migrate

app = FastAPI()

migrate()


app.include_router(v1.router)


def main():
    uvicorn.run("src.main:app", host="0.0.0.0", port=config.port, reload=config.debug)
