from app import create_app
from app.cache import cache
from app.log import log
from common.utils import get_current_time_date
from data.database import db
from data.queries import load_current_data
from fetchers.minzdrav import fetch_data

from data.models import CaseData, Location  # isort:skip


def update_data():
    app = create_app()

    with app.app_context():

        remote_data = fetch_data()
        current_data = load_current_data()
        now, today = get_current_time_date()

        updated_count = 0
        created_count = 0

        def create(record, location_id):
            confirmed = max(record["confirmed"], 0)
            recovered = max(record["recovered"], 0)
            fatal = max(record["fatal"], 0)

            if any([confirmed, recovered, fatal]):
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
                return 1
            return 0

        for location_name, record in remote_data.items():
            location_id = (
                Location.query.filter_by(minzdrav_name=location_name).first().id
            )

            current = current_data.get(location_name)

            if not current:
                created_count += create(record, location_id)
            else:
                keys = ["confirmed", "recovered", "fatal"]
                for k in keys:
                    record[k] = record[k] - current[k]

                if any(record[k] for k in keys):

                    instance = (
                        CaseData.query.filter_by(date=today)
                        .join(CaseData.location)
                        .filter_by(minzdrav_name=location_name)
                        .first()
                    )
                    if not instance:
                        created_count += create(record, location_id)
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
        if created_count or updated_count:
            cache.clear()
