# Browser Strategy Game

> A browser based strategy/MMORPG game, under development. 🚧

## Development

### Stack

These are the main packages used to develop this application.

- Python 3.12
- Poetry
- Ruff
- FastAPI
- SQLModel

### Getting started

Create a virtual environment and install dependencies:

```shell
python -m venv .venv
poetry env use .venv/bin/python
poetry install
```

Then, install pre-commit hooks:

```shell
poetry run pre-commit install
```

Finally, start the application:

```shell
poetry run python -m browserstrategygame.app
```

### Debugging

Add a debug configuration to VSCode:

```json
{
  "name": "Python Debugger: Remote Attach",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "localhost", "port": 5678 },
  "pathMappings": [{ "localRoot": "${workspaceFolder}", "remoteRoot": "." }]
}
```

Start the application with the debugger:

```shell
poetry run python -m debugpy --listen 5678 -m browserstrategygame.app
```

## License

Apache-2.0 ©️ 2024 Arthur Corenzan, Douglas Barbosa, etc.
