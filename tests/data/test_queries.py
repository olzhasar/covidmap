from data.factories import CaseDataFactory


def test_factory(with_context):
    record = CaseDataFactory(location_id=1, confirmed=100, recovered=50, fatal=0)

    assert record.confirmed == 100
    assert record.recovered == 50
    assert record.fatal == 0
