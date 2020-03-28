import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response, redirect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView as BaseModelView
from flask_basicauth import BasicAuth
from flask_caching import Cache
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

from config import Config

server = Flask(__name__)
server.config.from_object(Config)

cache = Cache(server)

auth = BasicAuth(server)

db = SQLAlchemy(server)
migrate = Migrate(server, db)

from models import CaseData, Location  # noqa E402 isort:skip

from updater import update_data  # noqa E402 isort:skip


if server.config["FETCH_ENABLED"]:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=update_data, trigger="interval", minutes=server.config["FETCH_INTERVAL"]
    )
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())


class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(
            message,
            response=Response(
                message, 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}
            ),
        )


@server.route("/logout")
def logout():
    raise AuthException("You have been logged out")


class ModelView(BaseModelView):
    def is_accessible(self):
        if not auth.authenticate():
            raise AuthException("Access denied")
        return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(auth.challenge())


admin = Admin(
    server,
    name="covidmap",
    template_mode="bootstrap3",
    url=f"/{server.config['ADMIN_URL']}",
)
admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(CaseData, db.session))
