import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from data import summary, table_data, updated_at
from figures import chart_fig, map_fig
from server import server

app = dash.Dash(
    "COVID-19 Map Kazakhstan",
    server=server,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
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
                            "Карта распространения коронавирусной инфекции COVID-19 в Казахстане",
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
                        html.H2(summary.confirmed, className="card-title danger"),
                        html.H3(
                            "Зарегистрированных случаев", className="card-subtitle",
                        ),
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        html.H2(summary.recovered, className="card-title success"),
                        html.H3("Выздоровевших", className="card-subtitle"),
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        html.H2(summary.fatal, className="card-title"),
                        html.H3("Летальных исходов", className="card-subtitle"),
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        html.P("Последнее обновление"),
                        html.H3(updated_at, className="card-subtitle"),
                    ],
                    className="card is-hidden-mobile",
                ),
            ],
            className="left-col",
        ),
        html.Div(children=[dcc.Graph(id="map", figure=map_fig),], className="main-col"),
        html.Div(
            children=[
                dash_table.DataTable(
                    id="cases-table",
                    columns=[{"name": i, "id": i} for i in table_data.columns],
                    data=table_data.to_dict("records"),
                    style_header={"fontWeight": "700",},
                    style_cell={
                        "backgroundColor": "#22252b",
                        "color": "#bdbdbd",
                        "border": "2px solid #1a1c23",
                        "textAlign": "left",
                        "fontFamily": "'Roboto Slabe', sans-serif",
                        "padding": "5px",
                    },
                ),
                dcc.Graph(id="dynamics-graph", figure=chart_fig),
            ],
            className="right-col",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H4(
                            "Сайт covidmap.kz создан исключительно в ознакомительных целях",
                        ),
                        html.P(
                            "Данные о зарегистрированных случаях берутся из открытых источников и обновляются по мере возможности. В связи с этим, данные на сайте могут иметь расхождение с реальными",
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
