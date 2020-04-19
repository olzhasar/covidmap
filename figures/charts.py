import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame

from server import cache

CHART_HOVER_TEMPLATE = "<b>%{y}</b> <br> %{x}<extra></extra>"

CHART_LAYOUT = dict(
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


@cache.memoize()
def render_confirmed_cumulative_chart(df: DataFrame):
    chart = go.Figure(layout=CHART_LAYOUT)
    chart.add_trace(
        go.Scatter(
            x=df.index,
            y=df.confirmed_cumulative,
            marker={"color": "rgba(255,170,0,0.7)"},
            mode="lines+markers",
            hovertemplate=CHART_HOVER_TEMPLATE,
        )
    )
    chart.update_layout(title={"text": "Всего случаев с 13.03.20"})
    chart.update_layout(
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
                    "size": 10,
                },
                bgcolor=None,
                bordercolor="#bdbdbd",
                borderwidth=1,
            ),
        ]
    )

    return chart


@cache.memoize()
def render_confirmed_daily_chart(df: DataFrame):
    chart = go.Figure(layout=CHART_LAYOUT)
    chart.add_trace(
        go.Bar(
            x=df.index,
            y=df.confirmed,
            marker={"color": "rgba(255,170,0,0.7)"},
            hovertemplate=CHART_HOVER_TEMPLATE,
        )
    )
    chart.update_layout(title={"text": "Количество новых случаев по дням"})

    return chart


@cache.memoize()
def render_confirmed_cumulative_by_region_chart(df: DataFrame):
    top_regions = (
        df.groupby("location_id")["confirmed"]
        .sum()
        .sort_values(ascending=False)
        .iloc[:5]
        .index
    )
    df = df.loc[top_regions].reset_index()[["confirmed_cumulative", "date", "name"]]

    chart = go.Figure(layout=CHART_LAYOUT)

    for name, current_df in df.groupby("name"):
        chart.add_trace(
            go.Scatter(
                x=current_df.date,
                y=current_df.confirmed_cumulative,
                name=name,
                mode="lines",
                hovertemplate=CHART_HOVER_TEMPLATE,
            )
        )
    chart.update_layout(
        title={"text": "Всего случаев в разрезе регионов (Топ 5)"},
        colorway=px.colors.qualitative.Bold,
        legend=dict(traceorder="reversed", x=0.05, y=1.0,),
    )

    return chart


@cache.memoize()
def render_daily_increase_chart(df: DataFrame):
    df["daily_increase"] = df.confirmed_cumulative.pct_change() * 100
    hover_template = "<b>%{text} %</b> <br> %{x}<extra></extra>"

    chart = go.Figure(layout=CHART_LAYOUT)
    chart.add_trace(
        go.Bar(
            x=df.index,
            y=df.daily_increase,
            text=df.daily_increase.round(2).astype(str),
            marker={"color": "rgba(255,170,0,0.7)"},
            hovertemplate=hover_template,
        )
    )
    chart.update_layout(title={"text": "Однодневный прирост в %"})

    return chart


@cache.memoize()
def render_recovered_cumulative_chart(df: DataFrame):
    df = df[df["recovered_cumulative"] > 0]

    chart = go.Figure(layout=CHART_LAYOUT)
    chart.add_trace(
        go.Scatter(
            x=df.index,
            y=df.recovered_cumulative,
            mode="lines+markers",
            marker={"color": "rgba(112,168,0,0.7)"},
            hovertemplate=CHART_HOVER_TEMPLATE,
        )
    )
    chart.update_layout(title={"text": "Всего выздоровевших"},)

    return chart


@cache.memoize()
def render_fatal_cumulative_chart(df: DataFrame):
    df = df[df["fatal_cumulative"] > 0]

    chart = go.Figure(layout=CHART_LAYOUT)
    chart.add_trace(
        go.Scatter(
            x=df.index,
            y=df.fatal_cumulative,
            mode="lines+markers",
            marker={"color": "#bdbdbd"},
            hovertemplate=CHART_HOVER_TEMPLATE,
        )
    )
    chart.update_layout(title={"text": "Всего смертей"},)

    return chart
