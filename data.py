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

    increase_series = df.drop(
        ["fatal", "location.latitude", "location.longitude"], axis=1
    ).set_index(["date", "location.name"])
    increase_series = increase_series.loc[
        increase_series.index.get_level_values(0)[-1]
    ]["confirmed"]

    current_data = (
        df.drop("date", axis=1)
        .groupby(["location.name", "location.latitude", "location.longitude"])
        .sum()
        .reset_index()
        .sort_values("confirmed", ascending=False)
    )

    current_data = current_data.merge(
        increase_series.rename("increase"),
        how="left",
        left_on="location.name",
        right_on="location.name",
    )

    def get_increase_str(x):
        if x > 0:
            return f"+{int(x)}"
        return None

    current_data["increase"] = current_data["increase"].apply(get_increase_str)

    summary = current_data[["confirmed", "recovered", "fatal"]].sum()

    historical_data = (
        df[["date", "confirmed", "recovered", "fatal"]].groupby("date").sum()
    )
    historical_data.index = pd.to_datetime(historical_data.index)

    start = df.date.min()
    end = df.date.max()
    date_range = pd.date_range(start, end)

    historical_data = historical_data.reindex(date_range).fillna(value=0).cumsum()

    updated_at = (
        CaseData.query.filter(CaseData.updated_at.isnot(None))
        .order_by(CaseData.updated_at.desc())
        .first()
        .updated_at.astimezone(pytz.timezone("Asia/Almaty"))
        .strftime("%d-%m-%Y %H:%M")
    )

    return current_data, historical_data, summary, updated_at
