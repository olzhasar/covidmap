import dash
import dash_core_components as dcc
import dash_html_components as html

from figures import get_charts, get_labels, get_map, get_table
from server import cache, server

external_scripts = []
if not server.debug:
    external_scripts.append(server.config["GA_URL"])

app = dash.Dash(
    "COVID-19 Map Kazakhstan",
    server=server,
    external_scripts=external_scripts,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {
            "name": "description",
            "content": "Количество зарегистрированных случаев заболевания коронавирусом по регионам. Динамика изменений",
        },
        {
            "name": "google-site-verification",
            "content": "nORpfyOs_-RD9ONCHwL0OM0R2E3vIioVYu1ea5Ecp2A",
        },
    ],
)

app.title = "Карта коронавирусной инфекции COVID-19 - Казахстан"
app.scripts.serve_locally = True


@cache.memoize()
def render_layout():
    map_fig = get_map()
    charts = get_charts()
    table = get_table()
    labels = get_labels()

    layout = html.Div(
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
                className="header is-hidden-mobile",
            ),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            labels["confirmed"],
                            html.H3(
                                "Зарегистрированных случаев", className="card-subtitle",
                            ),
                        ],
                        className="card",
                    ),
                    html.Div(
                        children=[
                            labels["recovered"],
                            html.H3("Выздоровевших", className="card-subtitle"),
                        ],
                        className="card",
                    ),
                    html.Div(
                        children=[
                            labels["fatal"],
                            html.H3("Летальных исходов", className="card-subtitle"),
                        ],
                        className="card",
                    ),
                    html.Div(
                        children=[
                            html.P("Последнее обновление"),
                            labels["updated_at"],
                        ],
                        className="card is-hidden-mobile",
                    ),
                ],
                className="summary",
            ),
            html.Div(
                children=[dcc.Graph(id="map", figure=map_fig), table,], className="main"
            ),
            html.Div(
                children=[
                    dcc.Graph(figure=charts["cumulative_linear"]),
                    dcc.Graph(figure=charts["cumulative_log"]),
                    dcc.Graph(figure=charts["daily_bar"]),
                    dcc.Graph(figure=charts["recovered_bar"]),
                ],
                className="charts",
            ),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.H4(
                                "Сайт covidmap.kz создан исключительно в информативных целях",
                            ),
                            html.P(
                                "Данные о зарегистрированных случаях берутся из официальных источников и обновляются в автоматическом режиме по мере публикации Министерством здравоохранения Республики Казахстан",
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
    return layout


app.layout = render_layout

if __name__ == "__main__":
    app.run_server()
