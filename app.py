import dash
import dash_core_components as dcc
import dash_html_components as html

from data import get_df, get_updated_at
from figures.charts import (
    render_confirmed_cumulative_by_region_chart,
    render_confirmed_cumulative_chart,
    render_confirmed_daily_chart,
    render_daily_increase_chart,
    render_fatal_cumulative_chart,
    render_recovered_cumulative_chart,
)
from figures.map import get_map
from figures.table import get_table
from server import cache, server

external_scripts = []
if not server.debug:
    external_scripts.append(server.config["GOOGLE_ANALYTICS_URL"])

META_TAGS = [
    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
    {"name": "description", "content": server.config["SEO_DESCRIPTION"],},
    {"name": "google-site-verification", "content": server.config["GOOGLE_META"],},
    {"property": "og:image", "content": "https://covidmap.kz/assets/covidmap.kz.jpg"},
    {"property": "og:image:type", "content": "image/jpeg"},
    {"property": "og:image:width", "content": "1905"},
    {"property": "og:image:height", "content": "1322"},
]

app = dash.Dash(
    "COVID-19 Map Kazakhstan",
    server=server,
    external_scripts=external_scripts,
    meta_tags=META_TAGS,
)

app.title = server.config["SEO_TITLE"]
app.scripts.serve_locally = True


@cache.memoize()
def render_layout():
    df = get_df()

    updated_at = get_updated_at()
    summary = df[["confirmed", "recovered", "fatal"]].sum()

    map_fig = get_map(df, updated_at)

    total_df = df.groupby("date").sum()

    confirmed_cumulative_chart = render_confirmed_cumulative_chart(total_df)
    confirmed_daily_chart = render_confirmed_daily_chart(total_df)
    recovered_cumulative_chart = render_recovered_cumulative_chart(total_df)
    daily_increase_chart = render_daily_increase_chart(total_df)
    fatal_cumulative_chart = render_fatal_cumulative_chart(total_df)
    confirmed_cumulative_by_region_chart = render_confirmed_cumulative_by_region_chart(
        df
    )

    table = get_table(df)

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
                className="summary",
            ),
            html.Div(
                children=[dcc.Graph(id="map", figure=map_fig, responsive=True), table],
                className="main",
            ),
            html.Div(
                children=[
                    dcc.Graph(figure=confirmed_cumulative_chart),
                    dcc.Graph(figure=confirmed_cumulative_by_region_chart),
                    dcc.Graph(figure=daily_increase_chart),
                    dcc.Graph(figure=confirmed_daily_chart),
                    dcc.Graph(figure=recovered_cumulative_chart),
                    dcc.Graph(figure=fatal_cumulative_chart),
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
