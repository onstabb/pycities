# -*- coding: utf-8 -*-
import os
import sqlite3
from typing import Sequence, Optional, Dict, Union, List

import config


def _init_table(conn: sqlite3.Connection, table_name: str, column_types: Dict[str, str]) -> None:
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    columns = ', '.join([f'{key} {value}' for key, value in column_types.items()])
    conn.execute(f"CREATE TABLE {table_name} ({columns})")


def data_loader(table_name: str, table_fields: Dict[str, str]):
    def decorator(func: callable):
        def wrapper(conn: sqlite3.Connection, filepath: Union[os.PathLike, str], *args, **kwargs):
            with open(filepath, "r", encoding="utf-8") as file:
                for line in file:
                    if line.startswith("#"):
                        continue

                    data = line.split("\t")
                    data[-1] = data[-1].replace("\n", "")
                    data = [item if item else None for item in data]
                    data = func(conn, data, *args, **kwargs)
                    if data is None:
                        continue

                    query = (f"INSERT INTO {table_name} ({','.join(table_fields.keys())}) "
                             f"VALUES ({','.join(['?'] * len(table_fields))})")
                    conn.execute(query, data)
                conn.commit()
        return wrapper
    return decorator


def init_country_table(conn: sqlite3.Connection) -> None:
    _init_table(conn, config.COUNTRY_TABLE_NAME, config.COUNTRIES_COLUMN_TYPES)


def init_administrative_table(conn: sqlite3.Connection) -> None:
    _init_table(conn, config.ADMINISTRATIVE_TABLE_NAME, config.ADMINISTRATIVE_COLUMN_TYPES)


def init_city_table(conn: sqlite3.Connection) -> None:
    _init_table(conn, config.CITY_TABLE_NAME, config.CITIES_COLUMN_TYPES)


def init_alternate_name_table(conn: sqlite3.Connection) -> None:
    _init_table(conn, config.ALTERNATE_NAME_TABLE_NAME, config.ALTERNATE_NAME_COLUMN_TYPES)
    conn.execute('DROP INDEX IF EXISTS geonames_ids_idx')
    conn.execute('CREATE INDEX "geonames_ids_idx" ON alternate_name("geonames_id")')


@data_loader(config.COUNTRY_TABLE_NAME, config.COUNTRIES_COLUMN_TYPES)
def load_country_data(_conn: sqlite3.Connection, row_data: List[str], *_args, **_kwargs) -> Optional[List[str]]:
    return row_data


@data_loader(config.ADMINISTRATIVE_TABLE_NAME, config.ADMINISTRATIVE_COLUMN_TYPES)
def load_administrative_data(conn: sqlite3.Connection, row_data: List[str], *_args, **_kwargs) -> Optional[List[str]]:
    country_code = row_data[0].split(".")[0]
    country_id = conn.execute(
        f"SELECT geonames_id FROM {config.COUNTRY_TABLE_NAME} WHERE iso = ?", (country_code,)
    ).fetchone()[0]
    row_data.append(country_id)
    return row_data


@data_loader(config.CITY_TABLE_NAME, config.CITIES_COLUMN_TYPES)
def load_city_data(conn: sqlite3.Connection, row_data: List[str], *_args, **_kwargs) -> Optional[List[str]]:
    admin_code, country_code = row_data[10], row_data[8]
    admin_key = f"{country_code}.{admin_code}"

    administrative_unit_id = conn.execute(
        f"SELECT geonames_id FROM {config.ADMINISTRATIVE_TABLE_NAME} WHERE key = ?", (admin_key,)
    ).fetchone()
    administrative_unit_id = administrative_unit_id[0] if administrative_unit_id else None
    country_id = conn.execute(
        f"SELECT geonames_id FROM {config.COUNTRY_TABLE_NAME} WHERE iso = ?", (country_code,)
    ).fetchone()[0]
    row_data.append(administrative_unit_id)
    row_data.append(country_id)
    return row_data


@data_loader(config.ALTERNATE_NAME_TABLE_NAME, config.ALTERNATE_NAME_COLUMN_TYPES)
def load_alternate_names(conn: sqlite3.Connection, row_data: List[str], *_args, **kwargs) -> Optional[List[str]]:
    geonames_id = row_data[1]
    languages: List[Union[str, None]] = kwargs.get("languages", [])
    languages.append(None)
    for table_name in (config.COUNTRY_TABLE_NAME, config.CITY_TABLE_NAME, config.ADMINISTRATIVE_TABLE_NAME):
        location_id = conn.execute(
            f"SELECT geonames_id FROM {table_name} WHERE geonames_id = ?", (geonames_id,)
        ).fetchone()
        location_id = location_id[0] if location_id else None
        if location_id and row_data[2] in languages:
            return row_data

    return None


def create_alternate_name_columns(conn: sqlite3.Connection, table_name: str, languages: Sequence[str]) -> None:
    for lang in languages:
        try:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN name_{lang} TEXT")
        except sqlite3.OperationalError as e:
            if not e.args[0].startswith("duplicate column name:"):
                raise e

        conn.execute(f"""

UPDATE {table_name} SET name_{lang} = (
    SELECT name FROM {config.ALTERNATE_NAME_TABLE_NAME} 
    WHERE geonames_id = {table_name}.geonames_id AND lang = \"{lang}\" AND is_historic IS NULL
    ORDER BY is_preferred DESC LIMIT 1
)
        """)

    conn.commit()


def create_city_names_fts(conn: sqlite3.Connection) -> None:
    conn.execute(f"DROP TABLE IF EXISTS {config.CITY_FTS_TABLE_NAME}")
    conn.execute(
        f"CREATE VIRTUAL TABLE {config.CITY_FTS_TABLE_NAME} "
        f"USING FTS5(name, geonames_id, tokenize='unicode61 remove_diacritics 1');"
    )
    conn.execute(
        f"INSERT INTO {config.CITY_FTS_TABLE_NAME}(name, geonames_id) "
        f"SELECT alternate_names, geonames_id FROM {config.CITY_TABLE_NAME} WHERE alternate_names IS NOT NULL;"
    )
    conn.execute(
        f"INSERT INTO {config.CITY_FTS_TABLE_NAME}(name, geonames_id) "
        f"SELECT name, geonames_id FROM {config.CITY_TABLE_NAME} WHERE alternate_names IS NULL;"
    )
    conn.commit()
