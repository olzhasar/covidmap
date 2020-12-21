import numpy as np
import pandas as pd
import pytz
from sqlalchemy import func

from app.cache import cache
from common.utils import get_current_time_date

from .models import CaseData, Location, db


@cache.memoize()
def load_df_from_db(end_date=None):
    query = CaseData.query
    if end_date:
        query = query.filter(CaseData.date <= end_date)

    fields = [
        "date",
        "confirmed",
        "recovered",
        "fatal",
        "location.id",
        "location.name",
        "location.latitude",
        "location.longitude",
    ]

    query = query.join(CaseData.location).values(*fields)

    df = pd.DataFrame(query, columns=fields)
    if not df.empty:
        df.sort_values("date", inplace=True)

    return df


@cache.memoize()
def get_locations():
    return Location.query.with_entities(Location.id).order_by("id").all()


@cache.memoize()
def get_locations_df():
    query = Location.query.with_entities(
        Location.id, Location.name, Location.latitude, Location.longitude
    )
    df = pd.DataFrame(query).set_index("id")
    return df


@cache.memoize()
def get_date_range(start_date=None, end_date=None):
    if not end_date:
        _, end_date = get_current_time_date()

    return pd.date_range(start_date, end_date)


@cache.memoize()
def get_df(end_date=None):
    query = CaseData.query
    if end_date:
        query = query.filter(CaseData.date <= end_date)
    query = (
        query.join(CaseData.location)
        .order_by("date")
        .values(
            "date",
            "confirmed",
            "recovered",
            "fatal",
            "location_id",
        )
    )
    df = pd.DataFrame(query)

    date_range = get_date_range(df.date.min(), end_date)
    locations = [i for i, in get_locations()]

    index = pd.MultiIndex.from_product(
        [locations, date_range], names=["location_id", "date"]
    )

    df = df.groupby(["location_id", "date"]).sum().reindex(index)
    df = df.fillna(0).astype("int32")

    locations_df = get_locations_df()

    df["confirmed_cumulative"] = df.groupby("location_id").confirmed.cumsum()
    df["recovered_cumulative"] = df.groupby("location_id").recovered.cumsum()
    df["fatal_cumulative"] = df.groupby("location_id").fatal.cumsum()

    df = df.merge(locations_df, left_on="location_id", right_index=True)

    return df


@cache.memoize()
def get_current_data(end_date=None):
    df = load_df_from_db(end_date)
    if df.empty:
        return df

    increase_series = df.drop(
        ["fatal", "location.latitude", "location.longitude"], axis=1
    ).set_index(["date", "location.name"])
    _, today = get_current_time_date()

    try:
        increase_series = increase_series.loc[today]["confirmed"]
    except KeyError:
        increased = False
    else:
        increased = True

    current_data = (
        df.drop("date", axis=1)
        .groupby(["location.name", "location.latitude", "location.longitude"])
        .sum()
        .reset_index()
        .sort_values("confirmed", ascending=False)
    )

    if increased:
        current_data = current_data.merge(
            increase_series.rename("increase"),
            how="left",
            left_on="location.name",
            right_on="location.name",
        )
    else:
        current_data["increase"] = 0

    def get_increase_str(x):
        if x > 0:
            return f"+{int(x)}"
        return None

    current_data["increase"] = current_data["increase"].apply(get_increase_str)

    current_data = current_data[current_data.confirmed > 0]

    return current_data


@cache.memoize()
def get_max_confirmed():
    current_data = get_current_data()
    return current_data["confirmed"].max()


@cache.memoize()
def get_summary():
    current_data = get_current_data()
    return current_data[["confirmed", "recovered", "fatal"]].sum()


@cache.memoize()
def get_date_range_unix(end_date=None):
    return get_date_range(end_date).astype(np.int64) // 10 ** 9


@cache.memoize()
def get_historical_data(end_date=None, location_id=None):
    df = load_df_from_db(end_date)

    date_range = get_date_range(end_date)
    columns = ["date", "confirmed", "recovered", "fatal"]

    if location_id:
        df = df[df["location.id"] == location_id]

    if df.empty:
        historical_data = pd.DataFrame(index=date_range, columns=columns)
    else:
        historical_data = df[columns].groupby("date").sum()
        historical_data.index = pd.to_datetime(historical_data.index)
        historical_data = historical_data.reindex(date_range).fillna(value=0)

    historical_data["growth_rate"] = historical_data.confirmed.pct_change()

    cumulative_data = historical_data.cumsum()

    recovered_data = historical_data["recovered"]
    recovered_positive = recovered_data[recovered_data > 0]
    if not recovered_positive.empty:
        recovered_data = recovered_data.loc[recovered_positive.index[0] :]

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


def load_current_data():
    session = db.session

    query = (
        session.query(
            func.sum(CaseData.confirmed),
            func.sum(CaseData.recovered),
            func.sum(CaseData.fatal),
            "location.minzdrav_name",
        )
        .join(CaseData.location)
        .group_by("location.minzdrav_name")
    )

    values_dict = {
        row[3]: {"confirmed": row[0], "recovered": row[1], "fatal": row[2]}
        for row in query
    }

    return values_dict
