import dash_core_components as dcc
import dash_html_components as html
from dash import Dash
from dash.dependencies import Input, Output

from .layout import render_layout


def create_dashboard(app):
    external_scripts = []
    if not app.debug:
        external_scripts.append(app.config["GOOGLE_ANALYTICS_URL"])

    META_TAGS = [
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {
            "name": "description",
            "content": app.config["SEO_DESCRIPTION"],
        },
        {
            "name": "google-site-verification",
            "content": app.config["GOOGLE_META"],
        },
        {
            "property": "og:image",
            "content": "https://covidmap.kz/assets/covidmap.kz.jpg",
        },
        {"property": "og:image:type", "content": "image/jpeg"},
        {"property": "og:image:width", "content": "1905"},
        {"property": "og:image:height", "content": "1322"},
    ]

    dashboard = Dash(
        "COVID-19 Map Kazakhstan",
        server=app,
        external_scripts=external_scripts,
        meta_tags=META_TAGS,
    )

    dashboard.layout = html.Div(
        children=[
            dcc.Input(id="reload_input", value=1, type="hidden"),
            html.Div(id="content"),
        ],
    )

    @dashboard.callback(Output("content", "children"), Input("reload_input", "value"))
    def render_content(input_value):
        with app.app_context():
            return render_layout()

    dashboard.title = app.config["SEO_TITLE"]
    dashboard.scripts.serve_locally = True

    return dashboard
