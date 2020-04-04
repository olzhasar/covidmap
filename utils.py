from datetime import datetime

import pandas as pd
import pytz


def datetime_to_unix(dt):
    return dt.astype(int) // 10 ** 9


def unix_to_datetime(unix):
    return pd.to_datetime(unix, unit="s")


def get_marks(date_range):
    result = {}
    for i, dt in enumerate(date_range):
        result[dt] = ""

    return result


def get_current_time_date():
    tz = pytz.timezone("Asia/Almaty")
    now = datetime.now(tz)
    return now, now.date()
