from fastapi import APIRouter

from . import players

router = APIRouter(
    prefix="/v1",
)

router.include_router(players.router)
