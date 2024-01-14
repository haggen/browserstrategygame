from datetime import datetime
from re import sub
from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

from . import config


@declared_attr
def __tablename__(cls) -> str:
    """
    Use snake_case for table names.
    """
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

    def delete(self):
        self.deleted_at = datetime.utcnow()

    @classmethod
    def not_deleted(cls):
        return cls.deleted_at == None  # noqa: E711

    def pay_stored_material(self, material_id: int, quantity: int):
        for storage in self.storage:
            if storage.material_id == material_id:
                if storage.balance >= quantity:
                    storage.balance -= quantity
                    return True

        return False


class Material(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    deleted_at: Optional[datetime] = None
    name: str
    storage: list["Storage"] = Relationship(back_populates="material")

    def delete(self):
        self.deleted_at = datetime.utcnow()

    @classmethod
    def not_deleted(cls):
        return cls.deleted_at == None  # noqa: E711


class Storage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(default=None, foreign_key="player.id")
    material_id: int = Field(default=None, foreign_key="material.id")
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
    buildings: "Building" = Relationship(back_populates="building_template")
    material_requirements: list["MaterialRequirement"] = Relationship(
        back_populates="building_template"
    )
    material_yields: list["MaterialYield"] = Relationship(
        back_populates="building_template"
    )

    def delete(self):
        self.deleted_at = datetime.utcnow()

    @classmethod
    def not_deleted(cls):
        return cls.deleted_at == None  # noqa: E711


class MaterialRequirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    deleted_at: Optional[datetime] = None
    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(
        back_populates="material_requirements"
    )
    material_id: int = Field(foreign_key="material.id")
    material: "Material" = Relationship()
    quantity: int

    def delete(self):
        self.deleted_at = datetime.utcnow()

    @classmethod
    def not_deleted(cls):
        return cls.deleted_at == None  # noqa: E711


class MaterialYield(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    deleted_at: Optional[datetime] = None
    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(
        back_populates="material_yields"
    )
    material_id: int = Field(foreign_key="material.id")
    material: "Material" = Relationship()
    quantity: int

    def delete(self):
        self.deleted_at = datetime.utcnow()

    @classmethod
    def not_deleted(cls):
        return cls.deleted_at == None  # noqa: E711


class Building(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    built_at: datetime = Field(default_factory=datetime.utcnow)
    destroyed_at: Optional[datetime] = None
    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(back_populates="buildings")
    player_id: int = Field(foreign_key="player.id")
    player: "Player" = Relationship(back_populates="buildings")

    @classmethod
    def not_destroyed(cls):
        return cls.destroyed_at == None  # noqa: E711

    def destroy(self):
        self.destroyed_at = datetime.utcnow()


# -
# -
# -

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
