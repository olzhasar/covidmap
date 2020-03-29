import pandas as pd
import pytz

from server import CaseData


def get_data():
    query = CaseData.query.join(CaseData.location).values(
        "date",
        "confirmed",
        "recovered",
        "fatal",
        "location.name",
        "location.latitude",
        "location.longitude",
    )
    df = pd.DataFrame(query)

    current_data = (
        df.drop("date", axis=1)
        .groupby(["location.name", "location.latitude", "location.longitude"])
        .sum()
        .reset_index()
        .sort_values("confirmed", ascending=False)
    )

    summary = current_data[["confirmed", "recovered", "fatal"]].sum()

    historical_data = (
        df[["date", "confirmed", "recovered", "fatal"]].groupby("date").sum()
    )
    historical_data.index = pd.to_datetime(historical_data.index)

    start = df.date.min()
    end = df.date.max()
    date_range = pd.date_range(start, end)

    historical_data = historical_data.reindex(date_range).fillna(value=0).cumsum()

    table_data = current_data[["location.name", "confirmed"]].sort_values(
        "confirmed", ascending=False
    )
    table_data.columns = ["Регион", "Случаев"]

    updated_at = (
        CaseData.query.filter(CaseData.updated_at.isnot(None))
        .order_by(CaseData.updated_at.desc())
        .first()
        .updated_at.astimezone(pytz.timezone("Asia/Almaty"))
        .strftime("%d-%m-%Y %H:%M")
    )

    return current_data, historical_data, table_data, summary, updated_at
