from datetime import datetime

import pytz

tz = pytz.timezone("Asia/Almaty")


def get_local_time():
    return datetime.now(tz)


def get_local_date():
    return get_local_time().date()


def localize_time(dt: datetime):
    return tz.localize(dt)
