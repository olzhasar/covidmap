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
import plotly.graph_objects as go
import plotly.express as px

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


def get_current_data():
    data = (
        CaseData.query.group_by("location_id")
        .join(CaseData.location)
        .values("confirmed", "location.name", "location.latitude", "location.longitude")
    )
    df = pd.DataFrame(data)
    return df


historical = get_historical_data()
df = get_current_data()
dates = historical.index.strftime("%Y-%m-%d").tolist()

# fig = go.Figure(
#     data=go.Scattergeo(
#         lat=df["location.latitude"],
#         lon=df["location.longitude"],
#         text=df["location.name"],
#         marker=dict(
#             size=df["confirmed"],
#             colorbar=dict(
#                 titleside="right",
#                 outlinecolor="rgba(68, 68, 68, 0)",
#                 ticks="outside",
#                 showticksuffix="last",
#                 dtick=0.1,
#             ),
#         ),
#     )
# )

fig = px.scatter_mapbox(
    df,
    lat="location.latitude",
    lon="location.longitude",
    hover_name="location.name",
    size="confirmed",
    zoom=4,
    height=800,
)


fig.update_layout(mapbox_style="carto-darkmatter")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

app = dash.Dash("Hello World", server=server)

app.layout = html.Div(
    children=[
        html.H1(children="COVIDMAP.kz", className="title"),
        dcc.Graph(id="graph", figure=fig),
        # dcc.Graph(
        #     id="example-graph",
        #     figure={
        #         "data": [
        #             {
        #                 "x": dates,
        #                 "y": historical.confirmed.tolist(),
        #                 "type": "bar",
        #                 "name": "Confirmed Cases",
        #             },
        #         ],
        #         "layout": {"title": "Dash Data Visualization"},
        #     },
        # ),
    ]
)


admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(CaseData, db.session))

if __name__ == "__main__":
    app.run_server()
