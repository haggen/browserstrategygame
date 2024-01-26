from datetime import datetime, UTC
from re import sub
from typing import Annotated, ClassVar, Optional, TypeVar

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import Field, Relationship, Session, SQLModel, col, create_engine

from browserstrategygame import config

T = TypeVar("T", bound=BaseModel)


class ModelBase(SQLModel):
    """
    Base our for database models.
    """

    @declared_attr
    def __tablename__(cls):
        """
        Use snake_case for table names.
        """

        return sub("(?!^)([A-Z]+)", r"_\1", cls.__name__).lower()

    def update(self, data: T):
        """
        Update model fields.
        """

        for key, value in data.model_dump().items():
            setattr(self, key, value)


class ModelId(SQLModel):
    """
    Id for primary key.
    """

    id: Optional[int] = Field(default=None, primary_key=True)


class ModelTimestamps(SQLModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
    )
    deleted_at: Optional[datetime] = None

    def delete(self):
        """
        Soft-delete the model.
        """

        self.update(deleted_at=datetime.now(UTC))

    @hybrid_property
    def not_deleted(self):
        """
        Check if the model is not deleted. Also works in queries.
        e.g. query(Model).where(Model.not_deleted)
        """

        return col(self.deleted_at) == None  # noqa: E711

    # Work around the issue of Pydantic trying to register it as a field.
    not_deleted: ClassVar[not_deleted]  # type: ignore


class Realm(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    A realm is a collection of players.
    """

    name: str
    players: list["Player"] = Relationship(back_populates="realm")
    building_templates: list["BuildingTemplate"] = Relationship(
        back_populates="realm"
    )


class Player(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    A player holds buildings and materials.
    """

    name: str
    buildings: list["Building"] = Relationship(back_populates="player")
    storage: list["Storage"] = Relationship(back_populates="player")
    realm_id: int = Field(foreign_key="realm.id")
    realm: "Realm" = Relationship(back_populates="players")

    def pay_stored_material(self, material_id: int, quantity: int):
        for storage in self.storage:
            if storage.material_id == material_id:
                if storage.balance >= quantity:
                    storage.balance -= quantity
                    return True

        return False


class Material(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    A material is a resource that can be produced, stored, and used to build buildings.
    """

    name: str


class Storage(ModelBase, table=True):
    """
    How much of a material a player has.
    """

    player_id: int = Field(default=None, foreign_key="player.id", primary_key=True)
    material_id: int = Field(default=None, foreign_key="material.id", primary_key=True)
    balance: int = 0
    player: "Player" = Relationship(back_populates="storage")
    material: "Material" = Relationship()


class BuildingTemplate(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    A building template is a blueprint for a building.
    """

    name: str
    buildings: "Building" = Relationship(back_populates="building_template")
    material_costs: list["MaterialCost"] = Relationship(
        back_populates="building_template",
    )
    material_yields: list["MaterialYield"] = Relationship(
        back_populates="building_template"
    )
    realm_id: int = Field(foreign_key="realm.id")
    realm: "Realm" = Relationship(back_populates="building_templates")


class MaterialCost(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    How much of a material a building costs to build.
    """

    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(
        back_populates="material_costs"
    )
    material_id: int = Field(foreign_key="material.id")
    material: "Material" = Relationship()
    quantity: int


class MaterialYield(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    How much of a material a building produces.
    """

    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(
        back_populates="material_yields"
    )
    material_id: int = Field(foreign_key="material.id")
    material: "Material" = Relationship()
    quantity: int


class Building(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    A building is a player-owned resource generator.
    """

    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(back_populates="buildings")
    player_id: int = Field(foreign_key="player.id")
    player: "Player" = Relationship(back_populates="buildings")


class Tick(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    When the game ticks, buildings produce materials, effects are applied, etc.
    """

    # Seconds between game ticks.
    LENGTH: ClassVar[int] = 60


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
        if db.get(Material, 1):
            return

        db.add(Realm(name="Realm - Cyber World"))

        stone = Material(name="Stone")
        db.add(stone)
        wood = Material(name="Wood")
        db.add(wood)
        iron = Material(name="Iron")
        db.add(iron)

        quarry = BuildingTemplate(name="Stone Quarry", realm_id=1)
        db.add(quarry)
        lumberyard = BuildingTemplate(name="Lumberyard", realm_id=1)
        db.add(lumberyard)
        iron_mine = BuildingTemplate(name="Iron Mine", realm_id=1)
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
