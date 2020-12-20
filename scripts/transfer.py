import os

from sqlalchemy import create_engine, select

from app.server import *

engine_lite = create_engine("sqlite:///db2.sqlite3")
engine_postgres = create_engine(os.getenv("POSTGRES_URL"))

with engine_lite.connect() as conn_lite:
    with engine_postgres.connect() as conn_cloud:
        for table in db.Model.metadata.sorted_tables:
            data = [dict(row) for row in conn_lite.execute(select(table.c))]
            conn_cloud.execute(table.insert().values(data))
