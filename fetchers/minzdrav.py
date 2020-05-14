import re

import requests
from bs4 import BeautifulSoup


def fetch_data():
    url = "https://www.coronavirus2020.kz/ru"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, features="lxml")

    # Confirmed

    data = {}

    def extract_from_div(parent_class, child_class, output_key):
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

    extract_from_div("last_info_covid_bl", "city_cov", "confirmed")
    extract_from_div("red_line_covid_bl", "city_cov", "recovered")
    extract_from_div("deaths_bl", "city_cov", "fatal")

    return data
