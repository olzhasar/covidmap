import dash_table
from pandas import DataFrame


def get_increase_str(x):
    if x > 0:
        return f"+{int(x)}"
    return None


def get_table(df: DataFrame):

    grouped = df[["confirmed", "name"]].groupby("name")

    df = grouped.sum()
    df["increase"] = grouped.last()
    df["increase"] = df["increase"].apply(get_increase_str)

    df.sort_values("confirmed", ascending=False, inplace=True)

    df.reset_index(inplace=True)

    table = dash_table.DataTable(
        id="cases-table",
        data=df.to_dict("records"),
        columns=[
            {"name": "Регион", "id": "name"},
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
        style_cell_conditional=[{"if": {"column_id": "name"}, "textAlign": "left",},],
        style_data_conditional=[
            {"if": {"column_id": "increase"}, "color": "rgb(250,170,0,0.7)",},
        ],
        editable=False,
        row_selectable=False,
        column_selectable=False,
    )

    return table
