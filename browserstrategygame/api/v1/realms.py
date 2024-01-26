from fastapi import APIRouter
from sqlmodel import select
from pydantic import BaseModel
from browserstrategygame.database import DatabaseDep, Realm

router = APIRouter(
    prefix="/realms",
    tags=["Realms"],
)


class BlankRealm(BaseModel):
    name: str


@router.get("")
def search_realms(db: DatabaseDep):
    query = select(Realm).where(Realm.not_deleted)
    realms = db.exec(query).all()
    return realms


@router.get("/{id}")
def get_realm(id: int, db: DatabaseDep):
    query = select(Realm).where(Realm.not_deleted, Realm.id == id)
    realm = db.exec(query).one()
    return realm
