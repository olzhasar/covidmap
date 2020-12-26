from datetime import date

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from data import queries
from data.models import CaseData
from tasks.update import compare_data, update_data
from tests.factories import CaseDataFactory, LocationFactory


class TestCompareData:
    def test_ok(self, use_db):
        old_data = {
            "Алматы": {
                "confirmed": 4,
                "recovered": 5,
                "fatal": 6,
            },
            "Астана": {
                "confirmed": 7,
                "recovered": 8,
                "fatal": 9,
            },
            "Шымкент": {
                "confirmed": 10,
                "recovered": 11,
                "fatal": 12,
            },
        }

        new_data = {
            "Алматы": {
                "confirmed": 14,
                "recovered": 25,
                "fatal": 36,
            },
            "Астана": {
                "confirmed": 17,
                "recovered": 28,
                "fatal": 39,
            },
            "Шымкент": {
                "confirmed": 40,
                "recovered": 11,
                "fatal": 32,
            },
        }

        diff = compare_data(old_data, new_data)

        assert diff == {
            "Алматы": {
                "confirmed": 10,
                "recovered": 20,
                "fatal": 30,
            },
            "Астана": {
                "confirmed": 10,
                "recovered": 20,
                "fatal": 30,
            },
            "Шымкент": {
                "confirmed": 30,
                "fatal": 20,
            },
        }


class TestUpdateTask:
    @pytest.fixture
    def locations(self):
        return [
            LocationFactory(id=1, minzdrav_name="Алматы"),
            LocationFactory(id=2, minzdrav_name="Астана"),
            LocationFactory(id=3, minzdrav_name="Шымкент"),
        ]

    @pytest.fixture
    def remote_data(self):
        return {
            "Алматы": {
                "confirmed": 11,
                "recovered": 12,
                "fatal": 13,
            },
            "Астана": {
                "confirmed": 21,
                "recovered": 22,
                "fatal": 23,
            },
            "Шымкент": {
                "confirmed": 31,
                "recovered": 32,
                "fatal": 33,
            },
        }

    @pytest.fixture
    def mock_remote_data(self, mocker: MockerFixture, remote_data):
        mock = mocker.patch("tasks.update.fetch_data")
        mock.return_value = remote_data
        return mock

    @pytest.fixture(autouse=True)
    def mock_send_telegram_message(self, mocker: MockerFixture):
        return mocker.patch("tasks.update.send_telegram_message")

    def test_no_old_data(
        self,
        app,
        use_db,
        locations,
        remote_data,
        mock_remote_data,
        mock_send_telegram_message,
    ):
        update_data()

        cases = CaseData.query.all()

        assert len(cases) == 3

        assert queries.load_current_data() == remote_data

        mock_send_telegram_message.assert_called_once()

    def test_same_data(
        self,
        app,
        use_db,
        remote_data,
        mock_remote_data,
        mock_send_telegram_message,
    ):
        CaseDataFactory(
            location__minzdrav_name="Алматы",
            confirmed=11,
            recovered=12,
            fatal=13,
        )
        CaseDataFactory(
            location__minzdrav_name="Астана",
            confirmed=21,
            recovered=22,
            fatal=23,
        )
        CaseDataFactory(
            location__minzdrav_name="Шымкент",
            confirmed=31,
            recovered=32,
            fatal=33,
        )

        update_data()

        cases = CaseData.query.all()

        assert len(cases) == 3

        assert queries.load_current_data() == remote_data

        mock_send_telegram_message.assert_not_called()

    @freeze_time("2020-12-12")
    def test_with_old_data_same_date(
        self, app, use_db, remote_data, mock_remote_data, mock_send_telegram_message
    ):
        CaseDataFactory(
            location__minzdrav_name="Алматы",
            confirmed=1,
            recovered=2,
            fatal=3,
            date=date(2020, 12, 12),
        )
        CaseDataFactory(
            location__minzdrav_name="Астана",
            confirmed=1,
            recovered=2,
            fatal=3,
            date=date(2020, 12, 12),
        )
        CaseDataFactory(
            location__minzdrav_name="Шымкент",
            confirmed=1,
            recovered=2,
            fatal=3,
            date=date(2020, 12, 12),
        )

        update_data()

        cases = CaseData.query.all()

        assert len(cases) == 3

        assert queries.load_current_data() == remote_data

        mock_send_telegram_message.assert_called_once()

    @freeze_time("2020-12-12")
    def test_with_old_data_diff_date(
        self, app, use_db, remote_data, mock_remote_data, mock_send_telegram_message
    ):
        CaseDataFactory(
            location__minzdrav_name="Алматы",
            confirmed=1,
            recovered=2,
            fatal=3,
            date=date(2020, 12, 10),
        )
        CaseDataFactory(
            location__minzdrav_name="Астана",
            confirmed=1,
            recovered=2,
            fatal=3,
            date=date(2020, 12, 10),
        )
        CaseDataFactory(
            location__minzdrav_name="Шымкент",
            confirmed=1,
            recovered=2,
            fatal=3,
            date=date(2020, 12, 10),
        )

        update_data()

        cases = CaseData.query.all()

        assert len(cases) == 6

        assert queries.load_current_data() == remote_data

        mock_send_telegram_message.assert_called_once()

    @freeze_time("2020-12-12")
    def test_remote_cases_greater_than_in_db(
        self, app, use_db, mock_remote_data, mock_send_telegram_message
    ):
        remote_data = {
            "Алматы": {
                "confirmed": 1,
                "recovered": 1,
                "fatal": 1,
            },
            "Астана": {
                "confirmed": 1,
                "recovered": 1,
                "fatal": 1,
            },
            "Шымкент": {
                "confirmed": 1,
                "recovered": 1,
                "fatal": 1,
            },
        }
        mock_remote_data.return_value = remote_data

        CaseDataFactory(
            location__minzdrav_name="Алматы",
            confirmed=1,
            recovered=1,
            fatal=1,
            date=date(2020, 12, 11),
        )
        CaseDataFactory(
            location__minzdrav_name="Астана",
            confirmed=1,
            recovered=1,
            fatal=1,
            date=date(2020, 12, 11),
        )
        CaseDataFactory(
            location__minzdrav_name="Шымкент",
            confirmed=1,
            recovered=1,
            fatal=1,
            date=date(2020, 12, 11),
        )
        CaseDataFactory(
            location__minzdrav_name="Алматы",
            confirmed=2,
            recovered=2,
            fatal=2,
            date=date(2020, 12, 12),
        )
        CaseDataFactory(
            location__minzdrav_name="Астана",
            confirmed=3,
            recovered=3,
            fatal=3,
            date=date(2020, 12, 12),
        )
        CaseDataFactory(
            location__minzdrav_name="Шымкент",
            confirmed=3,
            recovered=3,
            fatal=3,
            date=date(2020, 12, 12),
        )

        update_data()

        cases = CaseData.query.all()

        assert len(cases) == 3

        assert queries.load_current_data() == remote_data

        mock_send_telegram_message.assert_not_called()
