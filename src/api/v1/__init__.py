from fastapi import APIRouter

from . import building_templates, materials, players

router = APIRouter(
    prefix="/v1",
)

router.include_router(players.router)
router.include_router(materials.router)
router.include_router(building_templates.router)
