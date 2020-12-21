import pytest

from app.factory import create_app
from data.database import db


@pytest.fixture(scope="session")
def app():
    app = create_app(testing=True)
    yield app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def config(app):
    return app.config


@pytest.fixture(scope="function")
def use_db(app):
    with app.app_context():
        db.create_all()

        yield

        db.session.close()

        db.drop_all()
