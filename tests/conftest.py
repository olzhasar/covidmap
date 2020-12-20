import pytest

from server import server


@pytest.fixture
def client():
    return server.test_client()


@pytest.fixture
def config():
    return server.config
