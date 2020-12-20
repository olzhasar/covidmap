from flask import redirect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView as BaseModelView

from data.database import db
from data.models import CaseData, Location

from .auth import AuthException, auth
from .cache import cache


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
    name="covidmap",
    template_mode="bootstrap3",
    url="/admin",
)
admin.add_view(LocationModelView(Location, db.session))
admin.add_view(CaseDataModelView(CaseData, db.session))
