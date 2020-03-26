import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.graph_objects as go

from data import get_data
from server import server


def get_figures():
    current_data, historical_data, table_data, summary, updated_at = get_data()

    # map_fig = px.scatter_mapbox(
    #     current_data,
    #     lat="location.latitude",
    #     lon="location.longitude",
    #     hover_name="location.name",
    #     hover_data=["confirmed", "recovered", "fatal"],
    #     labels={
    #         "confirmed": "Зарегистрированных",
    #         "recovered": "Выздоровевших",
    #         "fatal": "Смертей",
    #     },
    #     size="confirmed",
    #     size_max=40,
    #     zoom=3.7,
    #     center={"lat": 48.0196, "lon": 66.9237},
    #     opacity=0.4,
    #     height=700,
    #     color_discrete_sequence=["rgb(230, 0, 0)"],
    # )

    # map_fig.data[
    #     0
    # ].hovertemplate = "<b>%{hovertext}</b><br><br>Зарегистрированных: %{customdata[0]}<br>Выздоровевших: %{customdata[1]}<br>Смертей: %{customdata[2]}"

    map_fig = go.Figure()

    map_fig.add_trace(
        go.Scattermapbox(
            lat=current_data["location.latitude"],
            lon=current_data["location.longitude"],
            mode="markers",
            marker=go.scattermapbox.Marker(
                color="rgb(230,0,0)",
                opacity=.4,
                size=current_data["confirmed"],
                sizemin=8,
            ),
            text=current_data['confirmed'],
        )
    )
    map_fig.update_layout(
        height=700,
        mapbox=dict(
            accesstoken=server.config["MAPBOX_TOKEN"],
            bearing=0,
            style=server.config["MAPBOX_STYLE_URL"],
            center=go.layout.mapbox.Center(lat=48.0196, lon=66.9237),
            zoom=3,
            pitch=0,
        ),
        hoverlabel={
            "bgcolor": "#1a1c23",
            "bordercolor": "#bdbdbd",
            "font": {
                "family": "'Roboto Slab', sans-serif",
                "color": "#bdbdbd",
                "size": 18,
            },
        },
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        font={"family": "'Roboto Slab', sans-serif", "color": "#bdbdbd"},
    )

    chart_fig = px.line(
        x=historical_data.index,
        y=historical_data.confirmed,
        color_discrete_sequence=["rgba(255, 170, 0, .7)"],
        height=400,
    )
    chart_fig.update_layout(
        dragmode=False,
        paper_bgcolor="#22252b",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel={
            "bgcolor": "#1a1c23",
            "bordercolor": "#bdbdbd",
            "font": {
                "family": "'Roboto Slab', sans-serif",
                "color": "#bdbdbd",
                "size": 18,
            },
        },
        grid=None,
        xaxis={
            "title": None,
            "showgrid": False,
            "nticks": 5,
            "tickformat": "%d.%m.%y",
        },
        yaxis={"title": "Общее количество случаев", "showgrid": False},
        font={"family": "'Roboto Slab', sans-serif", "color": "#bdbdbd"},
        margin={"r": 20, "t": 20, "l": 20, "b": 20},
    )

    chart_fig.data[0].hovertemplate = '%{x}:  <b style="color: rgb(230,0,0);">%{y}</b>'

    table = dash_table.DataTable(
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
    )
    confirmed_label = html.H2(summary.confirmed, className="card-title danger")
    recovered_label = html.H2(summary.recovered, className="card-title success")
    fatal_label = html.H2(summary.fatal, className="card-title")
    updated_at_label = html.H3(updated_at, className="card-subtitle")

    return (
        chart_fig,
        map_fig,
        table,
        confirmed_label,
        recovered_label,
        fatal_label,
        updated_at_label,
    )
