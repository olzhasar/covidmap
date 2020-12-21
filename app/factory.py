from flask import Flask

from data.database import db

from .admin import admin
from .auth import AuthException, auth
from .cache import cache
from .config import Config, TestConfig
from .migrate import migrate


def create_app(testing=False):
    app = Flask(__name__)

    config = TestConfig if testing else Config

    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app)
    cache.init_app(app)
    auth.init_app(app)
    admin.init_app(app)

    @app.route("/logout")
    def logout():
        raise AuthException("You have been logged out")

    return app
