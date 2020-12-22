import pytest
from pytest_mock import MockerFixture

from data import queries
from data.models import CaseData
from tasks.update import update_data
from tests.factories import CaseDataFactory, LocationFactory


class TestUpdateTask:
    @pytest.fixture
    def locations(self):
        LocationFactory(id=1, minzdrav_name="Алматы")
        LocationFactory(id=2, minzdrav_name="Астана")
        LocationFactory(id=3, minzdrav_name="Шымкент")

    @pytest.fixture
    def remote_data(self):
        return {
            "Алматы": {
                "confirmed": 150,
                "recovered": 250,
                "fatal": 10,
            },
            "Астана": {
                "confirmed": 250,
                "recovered": 350,
                "fatal": 7,
            },
            "Шымкент": {
                "confirmed": 180,
                "recovered": 201,
                "fatal": 4,
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

    @pytest.fixture
    def initial_data(self):
        pass

    def test_no_initial_data(self, use_db, locations, remote_data, mock_remote_data):
        update_data()

        cases = CaseData.query.all()

        assert len(cases) == 3

        assert queries.load_current_data() == remote_data
