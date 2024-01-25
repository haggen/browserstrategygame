from browserstrategygame import config, database

import uvicorn

database.connect(config.database_url)
database.migrate()
database.seed()

uvicorn.run(
    "browserstrategygame.app:app",
    host="0.0.0.0",
    port=config.port,
    reload=config.debug,
)
