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
poetry shell
poetry install
```

Then, assuming you're still in the virtual environment, configure pre-commit:

```shell
pre-commit install
```

Finally, start the application with the debugger:

```shell
python -m debugpy -l 5678 -m src
```

### VSCode

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

## License

Apache-2.0 ©️ 2024 Arthur Corenzan, Douglas Barbosa, etc.
