from datetime import date, datetime

import pytz

tz = pytz.timezone("Asia/Almaty")


def get_local_time() -> datetime:
    return datetime.now(tz)


def get_local_date() -> date:
    return get_local_time().date()


def localize_time(dt: datetime) -> datetime:
    return dt.astimezone(tz)
