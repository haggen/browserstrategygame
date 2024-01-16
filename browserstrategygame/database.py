from datetime import datetime
from re import sub
from typing import Annotated, Optional, TypeVar

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

from browserstrategygame import config


class Model(SQLModel):
    @declared_attr
    def __tablename__(cls):
        """
        Use snake_case for table names.
        """
        return sub("(?!^)([A-Z]+)", r"_\1", cls.__name__).lower()

    T = TypeVar("T", bound=BaseModel)

    def update(self, data: T):
        """
        Update a model with data from a Pydantic model.
        """
        for key, value in data.model_dump().items():
            setattr(self, key, value)


class Player(Model, table=True):
    """
    A player holds buildings and materials.
    """

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


class Material(Model, table=True):
    """
    A material is a resource that can be produced, stored, and used to build buildings.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    deleted_at: Optional[datetime] = None
    name: str

    def delete(self):
        self.deleted_at = datetime.utcnow()

    @classmethod
    def not_deleted(cls):
        return cls.deleted_at == None  # noqa: E711


class Storage(Model, table=True):
    """
    How much of a material a player has.
    """

    player_id: int = Field(default=None, foreign_key="player.id", primary_key=True)
    material_id: int = Field(default=None, foreign_key="material.id", primary_key=True)
    balance: int = 0
    player: "Player" = Relationship(back_populates="storage")
    material: "Material" = Relationship()


class BuildingTemplate(Model, table=True):
    """
    A building template is a blueprint for a building.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    deleted_at: Optional[datetime] = None
    name: str
    buildings: "Building" = Relationship(back_populates="building_template")
    material_costs: list["MaterialCost"] = Relationship(
        back_populates="building_template",
    )
    material_yields: list["MaterialYield"] = Relationship(
        back_populates="building_template"
    )

    def delete(self):
        self.deleted_at = datetime.utcnow()

    @classmethod
    def not_deleted(cls):
        return cls.deleted_at == None  # noqa: E711


class MaterialCost(Model, table=True):
    """
    How much of a material a building costs to build.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    deleted_at: Optional[datetime] = None
    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(
        back_populates="material_costs"
    )
    material_id: int = Field(foreign_key="material.id")
    material: "Material" = Relationship()
    quantity: int

    def delete(self):
        self.deleted_at = datetime.utcnow()

    @classmethod
    def not_deleted(cls):
        return cls.deleted_at == None  # noqa: E711


class MaterialYield(Model, table=True):
    """
    How much of a material a building produces.
    """

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


class Building(Model, table=True):
    """
    A building is a player-owned resource generator.
    """

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


class Tick(Model, table=True):
    """
    When the game ticks, buildings produce materials, effects are applied, etc.
    """

    # Seconds between game ticks.
    LENGTH = 60

    id: Optional[int] = Field(default=None, primary_key=True)
    ticked_at: datetime = Field(default_factory=datetime.utcnow)


# -
# -
# -

engine = create_engine(config.database_url, echo=True)


def migrate():
    """
    Create all tables in the database.
    """

    SQLModel.metadata.create_all(engine)


def seed():
    """
    Seed the database with initial data.
    """

    with Session(engine) as db:
        stone = Material(name="Stone")
        db.add(stone)
        wood = Material(name="Wood")
        db.add(wood)
        iron = Material(name="Iron")
        db.add(iron)

        quarry = BuildingTemplate(name="Stone Quarry")
        db.add(quarry)
        lumberyard = BuildingTemplate(name="Lumberyard")
        db.add(lumberyard)
        iron_mine = BuildingTemplate(name="Iron Mine")
        db.add(iron_mine)

        db.add(MaterialCost(building_template=iron_mine, material=stone, quantity=100))
        db.add(MaterialCost(building_template=iron_mine, material=wood, quantity=100))

        db.add(MaterialYield(building_template=quarry, material=stone, quantity=100))
        db.add(MaterialYield(building_template=lumberyard, material=wood, quantity=100))
        db.add(MaterialYield(building_template=iron_mine, material=iron, quantity=100))

        db.commit()


def yield_session():
    """
    FastAPI dependency to inject database session.
    """

    with Session(engine) as session:
        yield session


DatabaseDep = Annotated[Session, Depends(yield_session)]
