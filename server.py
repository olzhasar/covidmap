import logging

from flask import Flask, Response, redirect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView as BaseModelView
from flask_basicauth import BasicAuth
from flask_caching import Cache
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

from config import Config

log = logging.getLogger()

console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.INFO)

server = Flask(__name__)
server.config.from_object(Config)

cache = Cache(server)

auth = BasicAuth(server)

db = SQLAlchemy(server)
migrate = Migrate(server, db)

from data.models import CaseData, Location  # noqa E402 isort:skip


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


class CaseDataModelView(ModelView):
    column_default_sort = [("date", True), ("updated_at", True)]
    column_filters = ("location", "confirmed", "recovered", "fatal")

    def after_model_change(self, form, model, is_created):
        cache.clear()

    def after_model_delete(self, model):
        cache.clear()


class LocationModelView(ModelView):
    column_default_sort = "name"
    form_excluded_columns = ("CaseData",)

    def after_model_change(self, form, model, is_created):
        cache.clear()


admin = Admin(
    server,
    name="covidmap",
    template_mode="bootstrap3",
    url=f"/{server.config['ADMIN_URL']}",
)
admin.add_view(LocationModelView(Location, db.session))
admin.add_view(CaseDataModelView(CaseData, db.session))
