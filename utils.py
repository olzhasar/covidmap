import time

import pandas as pd


def datetime_to_unix(dt):
    return int(time.mktime(dt.timetuple()))


def unix_to_datetime(unix):
    return pd.to_datetime(unix, unit="s")


def get_marks(date_range):
    result = {}
    for i, date in enumerate(date_range):
        if i == 0 or i == len(date_range) - 1:
            result[datetime_to_unix(date)] = str(date.strftime("%d/%m"))
        else:
            result[datetime_to_unix(date)] = ""

    return result
