from datetime import datetime

import pytz
from sqlalchemy import func

from fetchers.minzdrav import fetch_data
from server import db, log, server

from models import CaseData, Location  # isort:skip


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


def get_time_date():
    tz = pytz.timezone("Asia/Almaty")
    now = datetime.now(tz)
    return now, now.date()


def update_data():
    remote_data = fetch_data()
    current_data = load_current_data()
    now, today = get_time_date()

    updated_count = 0
    created_count = 0

    def create(record, location_id):
        new = CaseData(
            location_id=location_id,
            confirmed=record["confirmed"],
            recovered=record["recovered"],
            fatal=record["fatal"],
            updated_at=now,
            date=today,
        )
        db.session.add(new)
        db.session.commit()

    for location_name, record in remote_data.items():
        location_id = Location.query.filter_by(minzdrav_name=location_name).first().id

        current = current_data.get(location_name)

        if not current:
            create(record, location_id)
            created_count += 1
        else:
            keys = ["confirmed", "recovered", "fatal"]
            for k in keys:
                record[k] = max(0, record[k] - current[k])

            if any(record[k] for k in keys):

                instance = (
                    CaseData.query.filter_by(date=today)
                    .join(CaseData.location)
                    .filter_by(minzdrav_name=location_name)
                    .first()
                )
                if not instance:
                    create(record, location_id)
                    created_count += 1
                else:
                    instance.confirmed += record["confirmed"]
                    instance.recovered += record["recovered"]
                    instance.fatal += record["fatal"]
                    instance.updated_at = now
                    db.session.commit()
                    updated_count += 1

    if created_count:
        log.info(f"Created {created_count} records")
    if updated_count:
        log.info(f"Updated {updated_count} records")
