import pandas as pd

from data import queries
from data.models import CaseData
from tests.factories import CaseDataFactory, LocationFactory


def test_factory(use_db):
    LocationFactory(id=1)

    CaseDataFactory(location_id=1, confirmed=100, recovered=50, fatal=0)

    record = CaseData.query.first()

    assert record
    assert record.confirmed == 100
    assert record.recovered == 50
    assert record.fatal == 0


class TestLoadFromDb:
    def test_empty(self, use_db):
        df = queries.load_df_from_db()

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_with_data(self, use_db):
        location = LocationFactory(id=1)

        records = CaseDataFactory.create_batch(5, location_id=1)
        records = sorted(records, key=lambda x: x.date)

        df = queries.load_df_from_db()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert list(df.columns) == [
            "date",
            "confirmed",
            "recovered",
            "fatal",
            "location.id",
            "location.name",
            "location.latitude",
            "location.longitude",
        ]

        i = 0
        for _, row in df.iterrows():
            record = records[i]

            assert row["date"] == record.date
            assert row["confirmed"] == record.confirmed
            assert row["recovered"] == record.recovered
            assert row["fatal"] == record.fatal
            assert row["location.id"] == location.id
            assert row["location.name"] == location.name
            assert row["location.latitude"] == float(location.latitude)
            assert row["location.longitude"] == float(location.longitude)

            i += 1
