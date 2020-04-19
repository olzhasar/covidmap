import plotly.graph_objects as go

from server import cache, server


@cache.memoize()
def get_map(df, updated_at=None):

    date_range = df.index.get_level_values(1).unique().sort_values()

    max_confirmed = df.confirmed_cumulative.max()

    hovertemplate = (
        "<b>  %{meta[0]}  </b><br>"
        + "<br>  <b style='color: rgb(200,0,0); font-size: 1.5rem; font-weight: 400;'>%{meta[1]}</b>  зарегистрированных  "
        + "<br>  <b style='color: rgb(112, 168, 0); font-size: 1.5rem; font-weight: 400'>%{meta[2]}</b>  выздоровевших  "
        + "<br>  <b style='font-size: 1.5rem; font-weight: 400'>%{meta[3]}</b>  смертей  "
        + "<extra></extra>"
    )

    def get_markers(current_df):
        confirmed = current_df[current_df.confirmed_cumulative > 0].confirmed_cumulative
        return go.Scattermapbox(
            lat=current_df.latitude,
            lon=current_df.longitude,
            text=confirmed.astype(str),
            textfont={
                "family": "'Roboto Slab', sans-serif",
                "color": "#bdbdbd",
                "size": 10,
            },
            meta=current_df[
                [
                    "name",
                    "confirmed_cumulative",
                    "recovered_cumulative",
                    "fatal_cumulative",
                ]
            ],
            hovertemplate=hovertemplate,
            mode="markers+text",
            marker=go.scattermapbox.Marker(
                color="rgb(230,0,0)",
                opacity=0.4,
                size=confirmed,
                sizemin=9,
                sizemode="area",
                sizeref=2 * max_confirmed / (60 ** 2),
            ),
        )

    frames = []

    sliders_dict = {
        "active": len(date_range) - 1,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {
                "size": 12,
                "family": "'Roboto Slab', sans-serif",
                "color": "#bdbdbd",
            },
            "prefix": "Дата:",
            "visible": True,
            "xanchor": "right",
            "offset": 20,
        },
        "transition": {"duration": 150, "easing": "elastic-in-out"},
        "pad": {"b": 10, "t": 20},
        "len": 0.9,
        "x": 0.05,
        "y": 0,
        "steps": [],
        "font": {
            "size": 10,
            "family": "'Roboto Slab', sans-serif",
            "color": "#bdbdbd",
        },
        "bgcolor": "#bdbdbd",
    }

    i = 1

    for dt, current_df in df.groupby(level=1):
        frames.append(go.Frame(data=[get_markers(current_df)], name=i))
        slider_step = {
            "args": [
                [i],
                {
                    "frame": {"duration": 500},
                    "mode": "immediate",
                    "transition": {"duration": 300, "easing": "quadratic-in-out"},
                },
            ],
            "label": dt.strftime("%d.%m.%y"),
            "method": "animate",
        }
        sliders_dict["steps"].append(slider_step)
        i += 1

    layout = dict(
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
            style=server.config["MAPBOX_STYLE_URL"],
            bearing=0,
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
        sliders=[sliders_dict],
        paper_bgcolor="#22252b",
    )

    layout["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [
                        None,
                        {
                            "frame": {"duration": 800},
                            "transition": {
                                "duration": 300,
                                "easing": "quadratic-in-out",
                            },
                        },
                    ],
                    "label": "Play",
                    "method": "animate",
                },
                {
                    "args": [
                        [None],
                        {
                            "frame": {"duration": 0},
                            "mode": "immediate",
                            "transition": {"duration": 0},
                        },
                    ],
                    "label": "Stop",
                    "method": "animate",
                },
            ],
            "direction": "right",
            "pad": {"t": 10},
            "showactive": False,
            "type": "buttons",
            "x": 0.05,
            "xanchor": "left",
            "y": 0,
            "yanchor": "top",
            "font": {
                "family": "'Roboto Slab', sans-serif",
                "color": "#bdbdbd",
                "size": 10,
            },
            "bordercolor": "#bdbdbd",
        }
    ]

    map_fig = go.Figure(data=get_markers(current_df), frames=frames, layout=layout)
    return map_fig
