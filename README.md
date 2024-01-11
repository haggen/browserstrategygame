# Browser Strategy Game

> ...

## Development

### Stack

- Python 3.12
- Poetry
- Ruff
- FastAPI
- SQLModel

### Getting started

Create a virtual environment and install dependencies:

```shell
python -m venv .venv
source .venv/bin/activate
poetry env use python
poetry install
poetry run pre-commit install
```

Start the application:

```shell
poetry run start
```

### Debugging with VSCode

Add debug configuration:

```json
{
  "name": "Python Debugger: Remote Attach",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "localhost", "port": 5678 },
  "pathMappings": [{ "localRoot": "${workspaceFolder}", "remoteRoot": "." }]
}
```

Start with debug:

> 💡 Debug mode defaults to on during development.

```shell
DEBUG=1 poetry run start
```

## License

Apache-2.0 ©️ 2024 Arthur Corenzan, Douglas Barbosa, etc.
