from fastapi import APIRouter

from . import (
    building_templates,
    buildings,
    material_costs,
    material_yields,
    materials,
    players,
    storage,
)

router = APIRouter(
    prefix="/v1",
)

router.include_router(building_templates.router)
router.include_router(buildings.router)
router.include_router(material_costs.router)
router.include_router(material_yields.router)
router.include_router(materials.router)
router.include_router(players.router)
router.include_router(storage.router)
router.include_router(storage.ticks)
