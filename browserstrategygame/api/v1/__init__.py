from fastapi import APIRouter

from . import (
    building_templates,
    buildings,
    material_effects,
    materials,
    players,
    realms,
    ticks,
    transactions,
)

router = APIRouter(
    prefix="/v1",
)

router.include_router(building_templates.router)
router.include_router(buildings.router)
router.include_router(material_effects.router)
router.include_router(materials.router)
router.include_router(players.router)
router.include_router(transactions.router)
router.include_router(ticks.router)
router.include_router(realms.router)
