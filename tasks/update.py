from typing import Dict

from app.cache import cache
from app.factory import create_app
from app.log import log
from common.utils import get_local_date
from data import queries, services
from fetchers.minzdrav import FetchParseError, FetchServerError, fetch_data
from tasks.telegram import send_telegram_message

Record = Dict[str, int]
DataDict = Dict[str, Record]


def _compare_records(existing: Record, new: Record) -> Record:
    result: Record = {}

    for field in ["confirmed", "recovered", "fatal"]:
        diff = new[field] - existing[field]

        if diff < 0:
            queries.delete_todays_data()
            raise ValueError(
                "Existing cases count is greater than remote\nDeleting today's data"
            )
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


def update_data():
    try:
        new_data = fetch_data(parser="html.parser")
    except FetchParseError as e:
        log.error(f"Failed to load remote data {e}")
        send_telegram_message(f"Update failed\n{e}")
        return
    except FetchServerError as e:
        log.error(f"Failed to load remote data {e}")
        return

    existing_data = queries.load_current_data()

    today = get_local_date()

    try:
        diff_data = compare_data(existing_data, new_data)
    except ValueError as e:
        log.error(e)
        return

    if not diff_data:
        return

    locations_mapping = queries.get_locations_minzdrav_name_mapping()

    message = "New data:\n"

    for location_name, record in diff_data.items():
        location_id = locations_mapping[location_name]

        services.update_or_create_record(
            location_id=location_id, record_date=today, **record
        )

        message += f"\n{location_name}:"
        for key, value in record.items():
            message += f"\n{key} - {value}"

    log.info(message)
    send_telegram_message(message)


def update_task():
    app = create_app()

    with app.app_context():
        update_data()

    cache_clear_result = cache.clear()
    log.info(f"Cache clear result: {cache_clear_result}")
