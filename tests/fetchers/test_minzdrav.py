import os

import pytest

from fetchers.minzdrav import fetch_data

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def mock_response(mocker):
    mock = mocker.patch("fetchers.minzdrav.requests.get")

    with open(os.path.join(CURRENT_DIR, "sample.html"), "r") as f:
        mock.return_value.text = f.read()

    return mock


def test_ok(mock_response):
    data = fetch_data(parser="html.parser")

    assert data == {
        "г. Нур-Султан": {
            "confirmed": 17719,
            "recovered": 16315,
            "fatal": 348,
        },
        "г. Алматы": {
            "confirmed": 17612,
            "recovered": 16254,
            "fatal": 359,
        },
        "г. Шымкент": {
            "confirmed": 5457,
            "recovered": 5285,
            "fatal": 78,
        },
        "Акмолинская область": {
            "confirmed": 6687,
            "recovered": 5581,
            "fatal": 92,
        },
        "Актюбинская область": {
            "confirmed": 3634,
            "recovered": 3490,
            "fatal": 39,
        },
        "Алматинская область": {
            "confirmed": 6556,
            "recovered": 5612,
            "fatal": 74,
        },
        "Атырауская область": {
            "confirmed": 12623,
            "recovered": 11813,
            "fatal": 92,
        },
        "Восточно-Казахстанская область": {
            "confirmed": 18354,
            "recovered": 14068,
            "fatal": 306,
        },
        "Жамбылская область": {
            "confirmed": 4858,
            "recovered": 4409,
            "fatal": 61,
        },
        "Западно-Казахстанская область": {
            "confirmed": 8867,
            "recovered": 7765,
            "fatal": 154,
        },
        "Карагандинская область": {
            "confirmed": 11730,
            "recovered": 11046,
            "fatal": 289,
        },
        "Костанайская область": {
            "confirmed": 6940,
            "recovered": 6699,
            "fatal": 29,
        },
        "Кызылординская область": {
            "confirmed": 3345,
            "recovered": 3287,
            "fatal": 15,
        },
        "Мангистауская область": {
            "confirmed": 3591,
            "recovered": 3500,
            "fatal": 55,
        },
        "Павлодарская область": {
            "confirmed": 8389,
            "recovered": 6703,
            "fatal": 69,
        },
        "Северо-Казахстанская область": {
            "confirmed": 8028,
            "recovered": 7128,
            "fatal": 41,
        },
        "Туркестанская область": {
            "confirmed": 3585,
            "recovered": 3472,
            "fatal": 46,
        },
    }
