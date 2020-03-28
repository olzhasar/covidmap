import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY", "COVIDSECRETSUPER123")
    SESSION_TYPE = "filesystem"

    FLASK_ADMIN_SWATCH = "cerulean"

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "POSTGRES_URL", "postgresql://covidmap:covidmap@localhost:5432/covidmap"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
    MAPBOX_STYLE_URL = os.getenv("MAPBOX_STYLE_URL", "dark")

    CACHE_TYPE = os.getenv("CACHE_TYPE", "redis")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", 600))
    CACHE_DIR = os.path.join(BASEDIR, "cache")

    BASIC_AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
    BASIC_AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "covidmap")

    ADMIN_URL = os.getenv("ADMIN_URL", "admin")

    FETCH_ENABLED = os.getenv("FETCH_ENABLED", False)
    FETCH_URL = os.getenv("FETCH_URL")
    FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", 10))
