from datetime import date, datetime

import pandas as pd
import pytest
import pytz
from freezegun import freeze_time

from data import queries
from data.models import CaseData
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


class TestGetLocationsMinzdravNameMapping:
    def test_no_data(self, use_db):
        mapping = queries.get_locations_minzdrav_name_mapping()

        assert mapping == {}

    def test_ok(self, use_db):
        LocationFactory(id=1, minzdrav_name="Almaty")
        LocationFactory(id=3, minzdrav_name="Astana")
        LocationFactory(id=55, minzdrav_name="Shymkent")

        mapping = queries.get_locations_minzdrav_name_mapping()

        assert mapping == {
            "Almaty": 1,
            "Astana": 3,
            "Shymkent": 55,
        }


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

    @pytest.mark.skip("Timezone problems")
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


@freeze_time("2020-12-12")
def test_delete_todays_data(use_db):
    today = date.today()

    CaseDataFactory.create_batch(5, date=today)
    CaseDataFactory.create_batch(5, date=date(2020, 11, 11))
    CaseDataFactory.create_batch(5, date=date(2020, 10, 10))

    assert CaseData.query.filter_by(date=today).count() == 5
    assert CaseData.query.count() == 15

    queries.delete_todays_data()

    assert CaseData.query.filter_by(date=today).count() == 0
    assert CaseData.query.count() == 10
