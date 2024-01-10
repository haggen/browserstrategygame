from sqlmodel import SQLModel, create_engine
from .. import config

engine = create_engine(config.database_url, echo=True)


def initialize():
    SQLModel.metadata.create_all(engine)
