import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

from data.database import db

from .admin import admin
from .auth import AuthException, auth
from .cache import cache
from .config import Config, TestConfig
from .migrate import migrate

if Config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
    )


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

    @app.route("/debug-sentry")
    def trigger_error():
        return 1 / 0

    return app
