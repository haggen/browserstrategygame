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
- SQLite

### Getting started

Install the dependencies. Poetry will create a virtual environment for us.

```shell
poetry install
```

If we're planning on making changes, we should also install pre-commit hooks.

```shell
poetry run pre-commit install
```

Finally, we start the application.

```shell
poetry run python -m browserstrategygame
```

### Debugging

Add a debug configuration to VSCode.

```json
{
  "name": "Python Debugger: Remote Attach",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "localhost", "port": 5678 },
  "pathMappings": [{ "localRoot": "${workspaceFolder}", "remoteRoot": "." }]
}
```

Start the debugger.

```shell
poetry run python -m debugpy --listen 5678 -m browserstrategygame
```

## License

Apache-2.0 ©️ 2024 Arthur Corenzan, Douglas Barbosa, etc.
