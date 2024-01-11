from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

from .. import config


engine = create_engine(config.database_url, echo=True)


def migrate():
    SQLModel.metadata.create_all(engine)


def yield_session():
    with Session(engine) as session:
        yield session


DatabaseDep = Annotated[Session, Depends(yield_session)]
