from datetime import date

import pandas as pd

from server import CaseData

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
)


summary = current_data[["confirmed", "recovered", "fatal"]].sum()


historical_data = df[["date", "confirmed", "recovered", "fatal"]].groupby("date").sum()
historical_data.index = pd.to_datetime(historical_data.index)

start = date(year=2020, month=3, day=1)
end = df.date.max()
date_range = pd.date_range(start, end)

historical_data = (
    historical_data.reindex(date_range).fillna(value=0).cumsum()
)
