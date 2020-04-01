import pandas as pd
import pytz

from server import CaseData, cache


@cache.memoize()
def load_df_from_db():
    query = CaseData.query.join(CaseData.location).values(
        "date",
        "confirmed",
        "recovered",
        "fatal",
        "location.name",
        "location.latitude",
        "location.longitude",
    )
    return pd.DataFrame(query)


@cache.memoize()
def get_current_data():
    df = load_df_from_db()

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

    return current_data, summary


@cache.memoize()
def get_historical_data():
    df = load_df_from_db()

    historical_data = (
        df[["date", "confirmed", "recovered", "fatal"]].groupby("date").sum()
    )
    historical_data.index = pd.to_datetime(historical_data.index)

    cumulative_data = historical_data.cumsum()

    recovered_data = historical_data["recovered"]
    first_recovered_date = recovered_data[recovered_data > 0].index[0]
    recovered_data = recovered_data.loc[first_recovered_date:]

    return historical_data, cumulative_data, recovered_data


@cache.memoize()
def get_updated_at():
    return (
        CaseData.query.filter(CaseData.updated_at.isnot(None))
        .order_by(CaseData.updated_at.desc())
        .first()
        .updated_at.astimezone(pytz.timezone("Asia/Almaty"))
        .strftime("%d-%m-%Y %H:%M")
    )
