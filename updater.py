from datetime import datetime

import pytz
import requests
from sqlalchemy import func

from server import db, server

from models import CaseData, Location  # isort:skip


def fetch_data():
    def not_null(record):
        return record["infected"] > 0 or record["deaths"] > 0 or record["recovered"] > 0

    response = requests.get(server.config["FETCH_URL"], verify=False)
    if not response.status_code == 200:
        raise Exception("Cannot download data")
    data = response.json()["cities"]

    return filter(not_null, data)


def load_current_data():
    session = db.session

    query = (
        session.query(
            func.sum(CaseData.confirmed),
            func.sum(CaseData.recovered),
            func.sum(CaseData.fatal),
            "location.api_id",
        )
        .join(CaseData.location)
        .group_by("location.api_id")
    )

    values_dict = {
        row[3]: {"confirmed": row[0], "recovered": row[1], "fatal": row[2]}
        for row in query
    }

    return values_dict


def get_time_date():
    tz = pytz.timezone("Asia/Almaty")
    now = datetime.now(tz)
    return now, now.date()


def update_data():
    remote_data = fetch_data()
    current_data = load_current_data()
    now, today = get_time_date()

    def create(record, location_id):
        new = CaseData(
            location_id=location_id,
            confirmed=record["infected"],
            recovered=record["recovered"],
            fatal=record["deaths"],
            updated_at=now,
        )
        db.session.add(new)

    for record in remote_data:
        location_id = Location.query.filter_by(api_id=record["id"]).first().id

        current = current_data.get(record["id"])
        commit = False

        if not current:
            create(record, location_id)
            commit = True
        else:
            confirmed_diff = max(0, record["infected"] - current["confirmed"])
            # recovered_diff = max(0, record["recovered"] - current["recovered"])
            recovered_diff = 0
            fatal_diff = max(0, record["deaths"] - current["fatal"])
            if any([confirmed_diff, recovered_diff, fatal_diff]):
                commit = True

                record["infected"] = confirmed_diff
                record["recovered"] = recovered_diff
                record["deaths"] = fatal_diff

                instance = (
                    CaseData.query.filter_by(date=today)
                    .join(CaseData.location)
                    .filter_by(api_id=record["id"])
                    .first()
                )
                if not instance:
                    create(record, location_id)
                else:
                    instance.confirmed += confirmed_diff
                    instance.recovered += recovered_diff
                    instance.fatal += fatal_diff
                    instance.updated_at = now
        if commit:
            db.session.commit()
