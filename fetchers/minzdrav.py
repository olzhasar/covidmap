import re

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

URL = "https://www.coronavirus2020.kz/ru"


class FetchServerError(Exception):
    pass


class FetchParseError(Exception):
    pass


def load_html():
    try:
        response = requests.get(URL, timeout=10)
    except RequestException as e:
        raise FetchServerError(str(e))

    return response.text


def extract_data(response_text: str, parser="parser.html"):
    soup = BeautifulSoup(response_text, features=parser)

    data = {}

    def _extract_from_div(parent_class, child_class, output_key):
        divs = (
            soup.find("div", {"class": parent_class})
            .find("div", {"class": child_class})
            .findAll("div")
        )
        rows = [d.text.strip() for d in divs]

        for row in rows:
            row = re.sub("[\(\[].*?[\)\]]", "", row)
            value = int("".join(filter(str.isdigit, row)))
            name = re.search("([^\d ]+ ?[^\d ]+)+", row).group(0).strip()

            record = data.get(name, {"confirmed": 0, "recovered": 0, "fatal": 0})
            record[output_key] = value

            data[name] = record

    divs = (
        ("last_info_covid_bl", "city_cov", "confirmed"),
        ("red_line_covid_bl", "city_cov", "recovered"),
        ("deaths_bl", "city_cov", "fatal"),
    )

    for row in divs:
        _extract_from_div(*row)

    return data


def fetch_data(parser="lxml"):
    html = load_html()

    try:
        data = extract_data(html, parser=parser)
    except Exception as e:
        raise FetchServerError(str(e))

    return data
