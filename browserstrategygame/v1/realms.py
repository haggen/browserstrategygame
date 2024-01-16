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


@router.post("")
def create_realm(data: BlankRealm, db: DatabaseDep):
    realm = Realm.model_validate(data)
    db.add(realm)
    db.commit()
    db.refresh(realm)
    return realm


@router.get("")
def search_realms(db: DatabaseDep):
    query = select(Realm).where(Realm.not_deleted())
    realms = db.exec(query).all()
    return realms

@router.get("/{id}")
def get_player(id: int, db: DatabaseDep):
    query = select(Realm).where(Realm.not_deleted(), Realm.id == id)
    realm = db.exec(query).one()
    return realm
