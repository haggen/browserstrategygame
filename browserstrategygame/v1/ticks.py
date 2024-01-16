from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm.exc import NoResultFound
from sqlmodel import col, select

from browserstrategygame.database import (
    Building,
    DatabaseDep,
    MaterialYield,
    Storage,
    Tick,
)

router = APIRouter(
    prefix="/ticks",
    tags=["Game"],
)


@router.get("")
def search_ticks(db: DatabaseDep):
    query = select(Tick).order_by(col(Tick.ticked_at).desc())
    return db.exec(query).all()


@router.get("/{tick_id}")
def get_tick(tick_id: int, db: DatabaseDep):
    query = select(Tick).where(Tick.id == tick_id)
    return db.exec(query).one()


@router.post("")
def create_tick(db: DatabaseDep):
    try:
        ticked_at = db.exec(
            select(Tick.ticked_at).order_by(col(Tick.ticked_at).desc()).limit(1)
        ).one()
    except NoResultFound:
        ticked_at = datetime.utcnow() - timedelta(seconds=Tick.LENGTH)

    tick = Tick(ticked_at=ticked_at + timedelta(seconds=Tick.LENGTH))

    if tick.ticked_at > datetime.utcnow():
        return JSONResponse(
            {"detail": f"Can only tick once every {Tick.LENGTH} seconds"},
            HTTPStatus.CONFLICT,
        )

    buildings = db.exec(select(Building).where(Building.not_destroyed())).all()

    for building in buildings:
        material_yields = db.exec(
            select(MaterialYield).where(
                MaterialYield.building_template_id == building.building_template_id
            )
        ).all()

        for material_yield in material_yields:
            try:
                storage = db.exec(
                    select(Storage).where(
                        Storage.player_id == building.player_id,
                        Storage.material_id == material_yield.material_id,
                    )
                ).one()
            except NoResultFound:
                storage = Storage(
                    player_id=building.player_id,
                    material_id=material_yield.material_id,
                    balance=0,
                )

            storage.balance += material_yield.quantity
            db.add(storage)

    db.add(tick)
    db.commit()
    db.refresh(tick)
    return tick
