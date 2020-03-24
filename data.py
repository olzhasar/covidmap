from datetime import date

import pandas as pd

from server import CaseData


def get_historical_data():
    query = CaseData.query
    df = pd.read_sql(query.statement, query.session.bind)
    df = df.drop(["id", "location_id"], axis=1).groupby("date").sum()

    start = date(year=2020, month=3, day=1)
    end = df.index.max()
    date_range = pd.date_range(start, end)

    df.sort_index(inplace=True)
    df = df.reindex(date_range, method="ffill").cumsum()
    df.fillna(inplace=True, value=0)

    return df


def get_current_data():
    data = (
        CaseData.query.group_by("location_id")
        .join(CaseData.location)
        .values(
            "confirmed",
            "recovered",
            "fatal",
            "location.name",
            "location.latitude",
            "location.longitude",
        )
    )
    df = pd.DataFrame(data)
    return df


historical = get_historical_data()
df = get_current_data()
dates = historical.index.strftime("%Y-%m-%d").tolist()
