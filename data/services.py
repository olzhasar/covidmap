from datetime import date, datetime

from data.database import db
from data.models import CaseData


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
