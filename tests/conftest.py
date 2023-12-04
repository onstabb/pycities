from pathlib import Path

import pytest


DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def data_dir():
    return DATA_DIR


@pytest.fixture(scope="module")
def temp_data_path(tmp_path_factory):
    return tmp_path_factory.mktemp("data",)


@pytest.fixture()
def languages():
    return ["uk", "pl", "en", "ru"]
