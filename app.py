from datetime import date

import pandas as pd
from flask import Flask, render_template
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


def get_historical_data():
    query = CaseData.query
    df = pd.read_sql(query.statement, query.session.bind)
    df = df.drop(["id", "location_id"], axis=1).groupby("date").sum()

    start = date(year=2020, month=3, day=1)
    end = df.index.max()
    date_range = pd.date_range(start, end)

    df = df.sort_index().reindex(date_range, method="ffill")
    df.fillna(inplace=True, value=0)

    return df.to_json(orient="index", date_format="iso")


@app.route("/")
def index():
    historical = get_historical_data()
    return render_template("index.html", historical=historical)


admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(CaseData, db.session))
