import pandas as pd
import pytz
from sqlalchemy import func

from app.cache import cache
from common.utils import get_current_time_date

from .models import CaseData, Location, db


@cache.memoize()
def get_locations_ids():
    locations = Location.query.with_entities(Location.id).order_by("id").all()
    return [row[0] for row in locations]


@cache.memoize()
def get_locations_df():
    fields = (
        "id",
        "name",
        "latitude",
        "longitude",
    )
    query = Location.query.with_entities(
        Location.id, Location.name, Location.latitude, Location.longitude
    )
    df = pd.DataFrame(query, columns=fields).set_index("id")
    return df


@cache.memoize()
def get_date_range(start_date=None, end_date=None):
    if not start_date:
        _, start_date = get_current_time_date()

    if not end_date:
        _, end_date = get_current_time_date()

    return pd.date_range(start_date, end_date)


def get_cases_df(end_date=None):
    query = CaseData.query
    if end_date:
        query = query.filter(CaseData.date <= end_date)

    fields = (
        "date",
        "confirmed",
        "recovered",
        "fatal",
        "location_id",
    )

    query = query.join(CaseData.location).order_by("date").values(*fields)

    return pd.DataFrame(query, columns=fields)


@cache.memoize()
def get_df(end_date=None):
    df = get_cases_df()

    if not df.empty:
        start_date = df.date.min()
    else:
        start_date = None

    date_range = get_date_range(start_date, end_date)
    locations_ids = get_locations_ids()

    index = pd.MultiIndex.from_product(
        [locations_ids, date_range], names=["location_id", "date"]
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
def get_updated_at():
    most_recent = (
        CaseData.query.filter(CaseData.updated_at.isnot(None))
        .order_by(CaseData.updated_at.desc())
        .first()
    )

    if not most_recent:
        return ""

    tz = pytz.timezone("Asia/Almaty")

    value = tz.localize(most_recent.updated_at)

    return value.strftime("%d-%m-%Y %H:%M")


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
