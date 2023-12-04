import sqlite3

import pytest

import config
import datadump


@pytest.fixture(scope="module")
def sqlite_conn(temp_data_path, data_dir):
    conn = sqlite3.connect(data_dir / "geonames_test.db")
    yield conn
    conn.close()


def test_load_countries(sqlite_conn, data_dir) -> None:
    datadump.init_country_table(sqlite_conn)
    datadump.load_country_data(sqlite_conn, data_dir / config.COUNTRIES_FILENAME)


def test_load_administrative(sqlite_conn, data_dir) -> None:
    datadump.init_administrative_table(sqlite_conn)
    datadump.load_administrative_data(sqlite_conn, data_dir / config.ADMINISTRATIVE_FILENAME)


def test_load_cities(sqlite_conn, data_dir) -> None:
    datadump.init_city_table(sqlite_conn)
    datadump.load_city_data(sqlite_conn, data_dir / config.CITIES_FILENAME)


def test_load_alternate_names(sqlite_conn, data_dir, languages) -> None:
    datadump.init_alternate_name_table(sqlite_conn)
    datadump.load_alternate_names(sqlite_conn, data_dir / config.ALTERNATE_NAMES_FILENAME, languages=languages)


@pytest.mark.parametrize(
    "table_name",
    argvalues=[config.COUNTRY_TABLE_NAME, config.ADMINISTRATIVE_TABLE_NAME, config.CITY_TABLE_NAME]
)
def test_create_alternate_name_columns(sqlite_conn, languages, table_name):
    datadump.create_alternate_name_columns(sqlite_conn, table_name, languages)


def test_create_city_names_fts(sqlite_conn):
    datadump.create_city_names_fts(sqlite_conn)

