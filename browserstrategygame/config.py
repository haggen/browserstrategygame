from os import environ

database_url = environ.get("DATABASE_URL", "sqlite:///development.db")
port = int(environ.get("PORT", 8000))
debug = bool(environ.get("DEBUG", True))
