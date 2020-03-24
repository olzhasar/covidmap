import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY", "COVIDSECRETSUPER123")
    SESSION_TYPE = "filesystem"
    FLASK_ADMIN_SWATCH = "cerulean"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASEDIR, "db.sqlite3")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
    MAPBOX_STYLE_URL = os.getenv("MAPBOX_STYLE_URL", "dark")
    CACHE_TYPE = "filesystem"
    CACHE_DEFAULT_TIMEOUT = 60
    CACHE_DIR = os.path.join(BASEDIR, 'cache')
