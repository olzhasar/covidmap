import plotly.express as px

from data import dates, df, historical
from server import server

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
