import uvicorn

from fastapi import FastAPI

from . import config
from .api import v1
from .database import migrate

app = FastAPI()
app.include_router(v1.router)

migrate()


def main():
    if config.debug:
        import debugpy

        debugpy.listen(("localhost", 5678))

    uvicorn.run("src.main:app", host="0.0.0.0", port=config.port, reload=config.debug)


if __name__ == "__main__":
    main()
