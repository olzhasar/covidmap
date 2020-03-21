import json

import pandas as pd
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
    df = pd.read_sql_table('case_data', con=db.engine)
    return df.to_json()


admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(CaseData, db.session))
