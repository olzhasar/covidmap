from datetime import datetime

import pandas as pd
import pytz

from data import queries
from tests.factories import CaseDataFactory, LocationFactory


class TestGetLocationsIds:
    def test_no_data(self, use_db):
        ids = queries.get_locations_ids()

        assert ids == []

    def test_ok(self, use_db):
        LocationFactory(id=1)
        LocationFactory(id=3)
        LocationFactory(id=55)
        LocationFactory(id=34)

        ids = queries.get_locations_ids()

        assert ids == [1, 3, 34, 55]


class TestGetLocationsDF:
    def test_no_data(self, use_db):
        df = queries.get_locations_df()

        assert df.empty
        assert list(df.columns) == ["name", "latitude", "longitude"]

    def test_ok(self, use_db):
        locations = LocationFactory.create_batch(5)

        df = queries.get_locations_df()

        assert not df.empty
        assert len(df) == 5

        i = 0
        for index, row in df.iterrows():
            location = locations[i]

            assert index == location.id
            assert row["name"] == location.name
            assert row["latitude"] == float(location.latitude)
            assert row["longitude"] == float(location.longitude)

            i += 1


class TestGetDF:
    def test_with_data(self, use_db):
        location = LocationFactory(id=1)

        records = CaseDataFactory.create_batch(5, location=location)
        records = sorted(records, key=lambda x: x.date)

        df = queries.get_df()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty

        assert list(df.index.names) == ["location_id", "date"]
        assert list(df.columns) == [
            "confirmed",
            "recovered",
            "fatal",
            "confirmed_cumulative",
            "recovered_cumulative",
            "fatal_cumulative",
            "name",
            "latitude",
            "longitude",
        ]


class TestGetUpdatedAt:
    def test_no_data(self, use_db):
        assert queries.get_updated_at() == ""

    def test_ok(self, use_db):
        dts = [
            datetime(2020, 1, 1, 12, 34, tzinfo=pytz.UTC),
            datetime(2020, 2, 1, 12, 34, tzinfo=pytz.UTC),
            datetime(2020, 3, 1, 12, 34, tzinfo=pytz.UTC),
            datetime(2020, 7, 1, 12, 34, tzinfo=pytz.UTC),
            datetime(2020, 5, 1, 12, 34, tzinfo=pytz.UTC),
            datetime(2020, 4, 1, 12, 34, tzinfo=pytz.UTC),
        ]

        for dt in dts:
            CaseDataFactory(updated_at=dt)

        assert queries.get_updated_at() == "01-07-2020 18:34"
