import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASEDIR, "db.sqlite3")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
