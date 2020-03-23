from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px

from config import Config

server = Flask(__name__)
server.config.from_object(Config)

admin = Admin(server, name="covidmap", template_mode="bootstrap3")

db = SQLAlchemy(server)
migrate = Migrate(server, db)

from models import CaseData, Location  # noqa E402


admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(CaseData, db.session))


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
        .values(
            "confirmed",
            "recovered",
            "fatal",
            "location.name",
            "location.latitude",
            "location.longitude",
        )
    )
    df = pd.DataFrame(data)
    return df


historical = get_historical_data()
df = get_current_data()
dates = historical.index.strftime("%Y-%m-%d").tolist()

map_fig = px.scatter_mapbox(
    df,
    lat="location.latitude",
    lon="location.longitude",
    hover_name="location.name",
    hover_data=["confirmed", "recovered", "fatal"],
    labels={
        "confirmed": "Зарегистрированных",
        "recovered": "Выздоровевших",
        "fatal": "Смертей",
    },
    size="confirmed",
    zoom=4,
    mapbox_style="dark",
    center={"lat": 48.0196, "lon": 66.9237},
    opacity=0.7,
    height=700,
    color_discrete_sequence=["rgba(230, 0, 0, .7)"],
)

map_fig.data[
    0
].hovertemplate = "<b>%{hovertext}</b><br><br>Зарегистрированных: %{customdata[0]}<br>Выздоровевших: %{customdata[1]}<br>Смертей: %{customdata[2]}"

map_fig.update_layout(
    mapbox_accesstoken=server.config["MAPBOX_TOKEN"],
    hoverlabel={
        "bgcolor": "#1a1c23",
        "bordercolor": "#bdbdbd",
        "font": {"family": "'Roboto Slab', sans-serif", "color": "#bdbdbd", "size": 18},
    },
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    font={"family": "'Roboto Slab', sans-serif", "color": "#bdbdbd"},
)


chart_fig = px.bar(
    x=dates,
    y=historical.confirmed.tolist(),
    color_discrete_sequence=["rgba(255, 170, 0, .7)"],
    height=700,
)
chart_fig.update_layout(
    paper_bgcolor="#22252b",
    plot_bgcolor="rgba(0,0,0,0)",
    grid=None,
    xaxis={"title": "Дата", "showgrid": False, "nticks": 5, "tickformat": "%d-%m"},
    yaxis={"title": "Общее количество случаев", "showgrid": False},
    font={"family": "'Roboto Slab', sans-serif", "color": "#bdbdbd"},
)

app = dash.Dash(
    "COVID-19 Map Kazakhstan",
    server=server,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.title = "Карта коронавирусной инфекции - Казахстан"
app.scripts.serve_locally = True

app.layout = html.Div(
    children=[
        html.Header(
            children=[
                html.Div(
                    children=[
                        html.H1(
                            "Интерактивная карта заражённости коронавирусом COVID-19 в Казахстане",
                            className="main-title",
                        ),
                    ],
                    className="box",
                )
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H2("58", className="card-title danger"),
                        html.H3(
                            "Зарегистрированных случаев", className="card-subtitle",
                        ),
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        html.H2("0", className="card-title success"),
                        html.H3("Выздоровевших", className="card-subtitle"),
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        html.H2("0", className="card-title"),
                        html.H3("Фатальных исходов", className="card-subtitle"),
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        html.P("Данные обновлены"),
                        html.H3("23.03.2020 23:17", className="card-subtitle"),
                    ],
                    className="card is-hidden-mobile",
                ),
            ],
            className="left-col",
        ),
        html.Div(children=[dcc.Graph(id="map", figure=map_fig),], className="main-col"),
        html.Div(
            children=[dcc.Graph(id="dynamics-graph", figure=chart_fig),],
            className="right-col",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.P(
                            "Интерактивная карта заражённости коронавирусом COVID-19 в Казахстане",
                            className="main-title",
                        ),
                    ],
                    className="box",
                )
            ],
            className="footer",
        ),
    ],
    className="dashboard",
)

if __name__ == "__main__":
    app.run_server()
