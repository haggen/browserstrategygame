from fastapi import APIRouter

from . import players
from . import turns

router = APIRouter(
    prefix="/v1",
)

router.include_router(players.router)
router.include_router(turns.router)
