import pytest


@pytest.fixture(autouse=True)
def config_path():
    return './test/crossbar.config.json'
