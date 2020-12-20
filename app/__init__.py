from data.database import db
from flask import Flask

from .admin import admin
from .auth import AuthException, auth
from .cache import cache
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    cache.init_app(app)
    auth.init_app(app)
    admin.init_app(app)

    @app.route("/logout")
    def logout():
        raise AuthException("You have been logged out")

    return app


if __name__ == "__main__":
    app = create_app()
