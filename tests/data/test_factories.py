from data.models import CaseData
from tests.factories import CaseDataFactory, LocationFactory


def test_factories(use_db):
    location = LocationFactory(id=4)

    CaseDataFactory(location=location, confirmed=100, recovered=50, fatal=0)

    record = CaseData.query.first()

    assert record
    assert record.confirmed == 100
    assert record.recovered == 50
    assert record.fatal == 0
    assert record.location_id == 4
