import json

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

admin = Admin(app, name="covidmap", template_mode="bootstrap3")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import CaseData, Location  # noqa E402


@app.route("/")
def index():
    data = CaseData.query.all()
    return json.dumps(data)


admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(CaseData, db.session))
