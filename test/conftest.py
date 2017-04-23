import pytest


def pytest_configure(config):
    pass


@pytest.fixture(autouse=True)
def config_path():
    return './test/crossbar.config.json'
