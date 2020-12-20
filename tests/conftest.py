import flask_migrate
import pytest
from app import create_app
from data.database import db


@pytest.fixture(scope="session")
def app():
    return create_app(testing=True)


@pytest.fixture(scope="session", autouse=True)
def _db(app):
    with app.app_context():
        flask_migrate.upgrade()

    yield

    with app.app_context():
        db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def config(app):
    return app.config
