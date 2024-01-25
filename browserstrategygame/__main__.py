from browserstrategygame import config

import uvicorn

uvicorn.run(
    "browserstrategygame.app:app",
    host="0.0.0.0",
    port=config.port,
    reload=config.debug,
)
