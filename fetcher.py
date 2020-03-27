import requests
from sqlalchemy import func

from server import db, server

from models import CaseData  # isort:skip


def fetch_data():
    response = requests.get(server.config["FETCH_URL"], verify=False)
    if not response.status_code == 200:
        raise Exception("Cannot download data")
    data = response.json()

    return data


def process_data(data: dict):
    pass


def load_data():
    session = db.session

    query = (
        session.query(
            func.sum(CaseData.confirmed),
            func.sum(CaseData.recovered),
            func.sum(CaseData.fatal),
            "location.api_id",
        )
        .join(CaseData.location)
        .group_by("location.api_id")
    )

    values_dict = {
        row[3]: {"confirmed": row[0], "recovered": row[1], "fatal": row[2],}
        for row in query
    }

    return values_dict
