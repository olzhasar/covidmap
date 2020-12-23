from datetime import date

from data.database import db
from data.models import CaseData


def update_or_create_record(*, location_id: int, record_date: date, **kwargs):
    instance = CaseData.query.filter_by(
        date=record_date, location_id=location_id
    ).first()

    if instance:
        for key, value in kwargs.items():
            old_val = getattr(instance, key)
            setattr(instance, key, old_val + value)

        db.session.commit()

        return instance, False

    instance = CaseData(
        date=record_date,
        location_id=location_id,
        **kwargs,
    )

    db.session.add(instance)
    db.session.commit()

    return instance, True
