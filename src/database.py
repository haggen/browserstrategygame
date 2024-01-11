from datetime import datetime
from re import sub
from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

from . import config


@declared_attr
def __tablename__(cls) -> str:
    return sub("(?!^)([A-Z]+)", r"_\1", cls.__name__).lower()


SQLModel.__tablename__ = __tablename__


class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    deleted_at: Optional[datetime] = None
    name: str
    buildings: list["Building"] = Relationship(back_populates="player")
    storage: list["Storage"] = Relationship(back_populates="player")


class Material(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    deleted_at: Optional[datetime] = None
    name: str
    storage: list["Storage"] = Relationship(back_populates="material")


class Storage(SQLModel, table=True):
    player_id: int = Field(default=None, foreign_key="player.id", primary_key=True)
    material_id: int = Field(default=None, foreign_key="material.id", primary_key=True)
    balance: int = 0
    player: "Player" = Relationship(back_populates="storage")
    material: "Material" = Relationship(back_populates="storage")


class BuildingTemplate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    deleted_at: Optional[datetime] = None
    name: str
    buildings: "Building" = Relationship(back_populates="template")
    requirements: list["Requirement"] = Relationship(back_populates="building_template")
    yields: list["Yield"] = Relationship(back_populates="building_template")


class Requirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(back_populates="requirements")
    material_id: int = Field(foreign_key="material.id")
    material: "Material" = Relationship(back_populates="requirements")
    quantity: int


class Yield(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(back_populates="yields")
    material_id: int = Field(foreign_key="material.id")
    material: "Material" = Relationship(back_populates="yields")
    quantity: int


class Building(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    built_at: datetime = Field(default_factory=datetime.utcnow)
    template_id: int = Field(foreign_key="building_template.id")
    template: "BuildingTemplate" = Relationship(back_populates="buildings")
    player_id: int = Field(foreign_key="player.id")
    player: "Player" = Relationship(back_populates="buildings")


def not_deleted(cls):
    return cls.deleted_at == None  # noqa: E711


engine = create_engine(config.database_url, echo=True)


def migrate():
    """
    Create all tables in the database.
    """
    SQLModel.metadata.create_all(engine)


def yield_session():
    """
    FastAPI dependency to inject database session.
    """
    with Session(engine) as session:
        yield session


DatabaseDep = Annotated[Session, Depends(yield_session)]
