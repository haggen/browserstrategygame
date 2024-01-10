from sqlmodel import Session, SQLModel, create_engine

from os import environ

connect_args = {"check_same_thread": False}
engine = create_engine(
    environ.get("DATABASE_URI"), echo=True, connect_args=connect_args
)


def initialize():
    SQLModel.metadata.create_all(engine)
