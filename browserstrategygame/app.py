from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import Response
from pydantic import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from browserstrategygame import config, database
from browserstrategygame.api import v1


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/teardown routine.
    """

    database.migrate()
    database.seed()

    yield


app = FastAPI(
    title="Browser Strategy Game API",
    debug=config.debug,
    lifespan=lifespan,
)
app.include_router(v1.router)


@app.exception_handler(ValidationError)
def handle_validation_error(req: Request, exception: ValidationError):
    return Response(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    )


@app.exception_handler(NoResultFound)
def handle_no_result_found(req: Request, exception: NoResultFound):
    return Response(
        status_code=HTTPStatus.NOT_FOUND,
    )
