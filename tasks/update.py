from datetime import date, datetime
from typing import Dict

from requests.exceptions import RequestException

from app.cache import cache
from app.factory import create_app
from app.log import log
from common.utils import get_current_time_date
from data import queries
from data.database import db
from data.models import CaseData
from fetchers.minzdrav import fetch_data
from tasks.telegram import send_telegram_message

Record = Dict[str, int]
DataDict = Dict[str, Record]


class UpdateError(Exception):
    pass


def _compare_records(existing: Record, new: Record) -> Record:
    result: Record = {}

    for field in ["confirmed", "recovered", "fatal"]:
        diff = new[field] - existing[field]

        if diff < 0:
            raise ValueError("Existing value is greater than new")
        if diff > 0:
            result[field] = diff

    return result


def compare_data(existing_data: DataDict, new_data: DataDict) -> DataDict:
    result: DataDict = {}

    for location_name, record in new_data.items():
        existing_record = existing_data.get(location_name)

        if not existing_record:
            result[location_name] = record
        else:
            diff = _compare_records(existing_record, record)
            if diff:
                result[location_name] = diff

    return result


def update_or_create_record(
    *, location_id: int, record_date: date, update_time: datetime, **kwargs
):
    instance = CaseData.query.filter_by(
        date=record_date, location_id=location_id
    ).first()

    if instance:
        for key, value in kwargs.items():
            old_val = getattr(instance, key)
            setattr(instance, key, old_val + value)

        instance.updated_at = update_time

        db.session.commit()

        return instance, False

    instance = CaseData(
        date=record_date,
        location_id=location_id,
        updated_at=update_time,
        **kwargs,
    )

    db.session.add(instance)
    db.session.commit()

    return instance, True


def update_data():
    try:
        new_data = fetch_data(parser="html.parser")
    except RequestException as e:
        log.error(f"Failed to load remote data {e}")
        send_telegram_message(f"Update failed\n{e}")
        return

    existing_data = queries.load_current_data()

    now, today = get_current_time_date()

    diff_data = compare_data(existing_data, new_data)

    if not diff_data:
        return

    locations_mapping = queries.get_locations_minzdrav_name_mapping()

    message = "New data:\n"

    for location_name, record in diff_data.items():
        location_id = locations_mapping[location_name]

        update_or_create_record(
            location_id=location_id, record_date=today, update_time=now, **record
        )

        message += f"\n{location_name}:"
        for key, value in record.items():
            message += f"\n{key} - {value}"

    log.info(message)
    send_telegram_message(message)

    cache.clear()


def update_task():
    app = create_app()

    with app.app_context():
        update_data()
