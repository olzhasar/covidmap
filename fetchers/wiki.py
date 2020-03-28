import locale
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


def fetch_wikipedia():
    url = "https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D1%81%D0%BF%D1%80%D0%BE%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5_COVID-19_%D0%B2_%D0%9A%D0%B0%D0%B7%D0%B0%D1%85%D1%81%D1%82%D0%B0%D0%BD%D0%B5"
    table_class = "wikitable ts-COVID-Хронология_распространения_в_Казахстане"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, features="lxml")
    table = soup.find("table", {"class": table_class})

    df = pd.read_html(str(table))[0]

    # Replace multiindex columns with single value
    df.columns = [c[1] for c in df.columns]

    # Drop last non-relevant row
    df = df[:-1]

    # Drop unused columns
    unused_cols = ["Всего", "Выздоровевшие", "Смерти", "Увеличение за день", "График"]
    df.drop(unused_cols, axis=1, inplace=True)

    df["Дата"] = df["Дата"].apply(lambda x: datetime.strptime(x, "%d %B %Y"))
    df.set_index("Дата", inplace=True)

    return df
