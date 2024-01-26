from datetime import datetime, UTC
from re import sub
from typing import Annotated, ClassVar, Optional, TypeVar

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

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

        return self.deleted_at == None  # noqa: E711

    # Work around the issue of Pydantic trying to register it as a field.
    not_deleted: ClassVar[not_deleted]  # type: ignore


class Realm(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    A realm is a collection of players.
    """

    name: str
    players: list["Player"] = Relationship(back_populates="realm")


class Player(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    A player holds buildings and materials.
    """

    name: str
    buildings: list["Building"] = Relationship(back_populates="player")
    transactions: list["MaterialTransaction"] = Relationship(back_populates="player")
    realm_id: int = Field(foreign_key="realm.id")
    realm: "Realm" = Relationship(back_populates="players")

    def transact(self, material_id: int, amount: int):
        """
        Transact material to/from the player.
        """

        # TODO: when amount is negative check if the player has enough materials.

        self.transactions.append(
            MaterialTransaction(
                player_id=self.id, material_id=material_id, amount=amount
            )
        )


class Material(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    A material is a resource that can be produced, stored, and used to build buildings.
    """

    name: str


class MaterialTransaction(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    Transaction of materials.
    """

    player_id: int = Field(default=None, foreign_key="player.id")
    player: "Player" = Relationship(back_populates="transactions")
    material_id: int = Field(default=None, foreign_key="material.id")
    material: "Material" = Relationship()
    amount: int = 0


class BuildingTemplate(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    A building template is a blueprint for a building.
    It defines the building's name and which material effects it has.
    """

    name: str
    buildings: "Building" = Relationship(back_populates="building_template")
    material_effects: list["MaterialEffect"] = Relationship(
        back_populates="building_template",
    )


class MaterialEffect(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    Event based material effects caused by buildings.

    For instance, a building will have negative material effects when it's built (building cost),
    but will also have a positive material effect when it ticks (material production).
    """

    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(
        back_populates="material_effects"
    )
    material_id: int = Field(foreign_key="material.id")
    material: "Material" = Relationship()
    event: str  # TODO: should be enum.
    amount: int


class Building(ModelBase, ModelId, ModelTimestamps, table=True):
    """
    A building is a player-owned resource generator.
    """

    building_template_id: int = Field(foreign_key="building_template.id")
    building_template: "BuildingTemplate" = Relationship(back_populates="buildings")
    player_id: int = Field(foreign_key="player.id")
    player: "Player" = Relationship(back_populates="buildings")

    def tick(self, ticked_at: datetime):
        """
        Apply material effects on tick.
        """

        for material_effect in self.building_template.material_effects:
            if material_effect.not_deleted and material_effect.event == "tick":
                self.player.transact(
                    material_effect.material_id, material_effect.amount
                )


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

        db.add(Realm(name="Kingdom of Death"))

        stone = Material(name="Stone")
        db.add(stone)
        wood = Material(name="Wood")
        db.add(wood)
        iron = Material(name="Iron")
        db.add(iron)

        quarry = BuildingTemplate(
            name="Stone Quarry",
            material_effects=[
                MaterialEffect(material=stone, event="tick", amount=1),
            ],
        )
        db.add(quarry)

        lumberyard = BuildingTemplate(
            name="Lumberyard",
            material_effects=[
                MaterialEffect(material=wood, event="tick", amount=1),
            ],
        )
        db.add(lumberyard)

        iron_mine = BuildingTemplate(
            name="Iron Mine",
            material_effects=[
                MaterialEffect(material=stone, event="build", amount=-10),
                MaterialEffect(material=wood, event="build", amount=-10),
                MaterialEffect(material=iron, event="tick", amount=1),
            ],
        )
        db.add(iron_mine)

        db.commit()


def yield_session():
    """
    FastAPI dependency to inject database session.
    """

    with Session(engine) as session:
        yield session


DatabaseDep = Annotated[Session, Depends(yield_session)]
