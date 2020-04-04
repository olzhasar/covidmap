import dash_html_components as html
import dash_table
import numpy as np
import plotly.graph_objects as go

from data import (
    get_current_data,
    get_historical_data,
    get_max_confirmed,
    get_summary,
    get_updated_at,
)
from server import cache, server


@cache.memoize()
def get_map(end_date=None):

    current_data = get_current_data(end_date)
    updated_at = get_updated_at()

    max_confirmed = get_max_confirmed()

    hovertemplate = (
        "<b>  %{meta[0]}  </b><br>"
        + "<br>  <b style='color: rgb(200,0,0); font-size: 1.5rem; font-weight: 400;'>%{meta[1]}</b>  зарегистрированных  "
        + "<br>  <b style='color: rgb(112, 168, 0); font-size: 1.5rem; font-weight: 400'>%{meta[2]}</b>  выздоровевших  "
        + "<br>  <b style='font-size: 1.5rem; font-weight: 400'>%{meta[3]}</b>  смертей  "
        + "<extra></extra>"
    )

    map_fig = go.Figure()

    if not current_data.empty:
        map_fig.add_trace(
            go.Scattermapbox(
                lat=current_data["location.latitude"],
                lon=current_data["location.longitude"],
                text=current_data["confirmed"].astype("str"),
                textfont={
                    "family": "'Roboto Slab', sans-serif",
                    "color": "#bdbdbd",
                    "size": 10,
                },
                meta=current_data[["location.name", "confirmed", "recovered", "fatal"]],
                hoverinfo="text",
                hovertemplate=hovertemplate,
                mode="markers+text",
                marker=go.scattermapbox.Marker(
                    color="rgb(230,0,0)",
                    opacity=0.4,
                    size=current_data["confirmed"],
                    sizemin=9,
                    sizemode="area",
                    sizeref=2 * max_confirmed / (60 ** 2),
                ),
            )
        )

    else:
        map_fig.add_trace(go.Scattermapbox(lat=[], lon=[],))

    map_fig.update_layout(
        title={
            "text": f"Данные обновлены: {updated_at}",
            "x": 0.5,
            "y": 0.98,
            "font": {
                "family": "'Roboto Slab', sans-serif",
                "color": "rgba(189,189,189,0.7)",
                "size": 10,
            },
        },
        mapbox=dict(
            accesstoken=server.config["MAPBOX_TOKEN"],
            bearing=0,
            style=server.config["MAPBOX_STYLE_URL"],
            center=go.layout.mapbox.Center(lat=48.0196, lon=66.9237),
            zoom=3,
            pitch=0,
        ),
        showlegend=False,
        hoverlabel={
            "bgcolor": "#1a1c23",
            "bordercolor": "#bdbdbd",
            "align": "auto",
            "font": {
                "family": "'Roboto Slab', sans-serif",
                "color": "#bdbdbd",
                "size": 18,
            },
        },
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        font={"family": "'Roboto Slab', sans-serif", "color": "#bdbdbd"},
    )

    return map_fig


@cache.memoize()
def get_charts():

    historical_data, cumulative_data, recovered_data = get_historical_data()

    chart_hov_template = "<b>%{y}</b> <br> %{x}<extra></extra>"
    chart_layout = dict(
        dragmode=False,
        paper_bgcolor="#22252b",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel={
            "bgcolor": "#1a1c23",
            "bordercolor": "#bdbdbd",
            "font": {
                "family": "'Roboto Slab', sans-serif",
                "color": "#bdbdbd",
                "size": 14,
            },
            "align": "left",
        },
        grid=None,
        xaxis={
            "title": None,
            "type": "date",
            "showgrid": False,
            "showline": False,
            "nticks": 10,
            "tickformat": "%d/%m",
            "ticks": "outside",
        },
        yaxis={"showgrid": False, "zeroline": False},
        font={"family": "'Roboto Slab', sans-serif", "color": "#bdbdbd", "size": 10},
        title={"x": 0.5, "y": 1, "pad": {"r": 0, "t": 20, "l": 0, "b": 20}},
        height=350,
        margin={"r": 40, "t": 80, "l": 40, "b": 40},
    )

    charts = {}

    charts["cumulative_linear"] = go.Figure(layout=chart_layout)
    charts["cumulative_linear"].add_trace(
        go.Scatter(
            x=cumulative_data.index,
            y=cumulative_data.confirmed,
            marker={"color": "rgba(255,170,0,0.7)"},
            hovertemplate=chart_hov_template,
        )
    )
    charts["cumulative_linear"].update_layout(
        title={"text": "Всего случаев с 13.03.20"}
    )

    charts["cumulative_linear"].update_layout(
        updatemenus=[
            dict(
                buttons=list(
                    [
                        dict(
                            args=[
                                {
                                    "yaxis": {
                                        "type": "linear",
                                        "showgrid": False,
                                        "zeroline": False,
                                    }
                                }
                            ],
                            label="Линейная шкала",
                            method="relayout",
                        ),
                        dict(
                            args=[
                                {
                                    "yaxis": {
                                        "type": "log",
                                        "showgrid": False,
                                        "zeroline": False,
                                    }
                                }
                            ],
                            label="Логарифм. шкала",
                            method="relayout",
                        ),
                    ]
                ),
                type="buttons",
                direction="right",
                showactive=False,
                x=0.5,
                xanchor="center",
                y=1.15,
                yanchor="top",
                pad={"r": 0, "t": 0, "l": 0, "b": 20},
                font={
                    "family": "'Roboto Slab', sans-serif",
                    "color": "#bdbdbd",
                    "size": 12,
                },
                bgcolor=None,
                bordercolor="#bdbdbd",
                borderwidth=1,
            ),
        ]
    )

    charts["daily_bar"] = go.Figure(layout=chart_layout)
    charts["daily_bar"].add_trace(
        go.Bar(
            x=historical_data.index,
            y=historical_data.confirmed,
            marker={"color": "rgba(255,170,0,0.7)"},
            hovertemplate=chart_hov_template,
        )
    )
    charts["daily_bar"].update_layout(
        title={"text": "Количество новых случаев по дням"}
    )

    charts["recovered_bar"] = go.Figure(layout=chart_layout)
    charts["recovered_bar"].add_trace(
        go.Bar(
            x=recovered_data.index,
            y=recovered_data,
            text=recovered_data.replace({0: np.nan}),
            textposition="outside",
            textfont={
                "family": "'Roboto Slab', sans-serif",
                "color": "#bdbdbd",
                "size": 10,
            },
            marker={"color": "rgba(112,168,0,0.7)"},
            hovertemplate=chart_hov_template,
        )
    )
    charts["recovered_bar"].update_layout(
        title={"text": "Количество выздоровевших по дням"},
    )

    return charts


@cache.memoize()
def get_table():
    current_data = get_current_data()

    table = dash_table.DataTable(
        id="cases-table",
        data=current_data[["location.name", "confirmed", "increase"]].to_dict(
            "records"
        ),
        columns=[
            {"name": "Регион", "id": "location.name"},
            {"name": "Случаев", "id": "confirmed"},
            {"name": "За сегодня", "id": "increase"},
        ],
        merge_duplicate_headers=True,
        style_header={"fontWeight": "700", "whiteSpace": "normal", "height": "auto",},
        style_data={"whiteSpace": "normal", "height": "auto",},
        style_cell={
            "backgroundColor": "#22252b",
            "color": "#bdbdbd",
            "border": "2px solid #1a1c23",
            "textAlign": "right",
            "fontFamily": "'Roboto Slab', sans-serif",
            "padding": "5px",
        },
        style_cell_conditional=[
            {"if": {"column_id": "location.name"}, "textAlign": "left",},
        ],
        style_data_conditional=[
            {"if": {"column_id": "increase"}, "color": "rgb(250,170,0,0.7)",},
        ],
        editable=False,
        row_selectable=False,
        column_selectable=False,
    )

    return table


@cache.memoize()
def get_labels():
    summary = get_summary()
    updated_at = get_updated_at()

    labels = {
        "confirmed": html.H2(summary.confirmed, className="card-title danger"),
        "recovered": html.H2(summary.recovered, className="card-title success"),
        "fatal": html.H2(summary.fatal, className="card-title"),
        "updated_at": html.H3(updated_at, className="card-subtitle"),
    }

    return labels
