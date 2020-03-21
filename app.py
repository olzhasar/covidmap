from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

server = Flask(__name__)
server.config.from_object(Config)

admin = Admin(server, name="covidmap", template_mode="bootstrap3")

db = SQLAlchemy(server)
migrate = Migrate(server, db)

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

    return df


historical = get_historical_data()
dates = historical.index.strftime("%Y-%m-%d").tolist()


app = dash.Dash("Hello World", server=server)

app.layout = html.Div(
    children=[
        html.H1(children="COVIDMAP.kz"),
        dcc.Graph(
            id="example-graph",
            figure={
                "data": [
                    {
                        "x": dates,
                        "y": historical.confirmed.tolist(),
                        "type": "bar",
                        "name": "Confirmed Cases",
                    },
                ],
                "layout": {"title": "Dash Data Visualization"},
            },
        ),
    ]
)


admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(CaseData, db.session))

if __name__ == "__main__":
    app.run_server()
