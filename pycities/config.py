# -*- coding: utf-8 -*-
from pathlib import Path


GEONAMES_URL = "https://download.geonames.org/export/dump/"
DATA_DIR = Path(__file__).parent / "data"
DEFAULT_DATA_SOURCE = DATA_DIR / "data.db"

COUNTRIES_FILENAME = "countryInfo.txt"
ADMINISTRATIVE_FILENAME = "admin1CodesASCII.txt"
CITIES_FILENAME, CITIES_ARCHIVE_FILENAME = "cities15000.txt", "cities15000.zip"
ALTERNATE_NAMES_FILENAME, ALTERNATE_NAMES_ARCHIVE_FILENAME = "alternateNamesV2.txt", "alternateNamesV2.zip"

CITY_TABLE_NAME, CITY_FTS_TABLE_NAME = "city", "city_fts"
ADMINISTRATIVE_TABLE_NAME = "administrative_unit"
COUNTRY_TABLE_NAME = "country"
ALTERNATE_NAME_TABLE_NAME = "alternate_name"


ADMINISTRATIVE_COLUMN_TYPES = {
    "key": "TEXT NOT NULL UNIQUE",
    "name": "TEXT NOT NULL",
    "ascii_name": "TEXT NOT NULL",
    "geonames_id": "INTEGER NOT NULL UNIQUE PRIMARY KEY",
    "country_id": f"INTEGER NOT NULL REFERENCES {COUNTRY_TABLE_NAME}(geonames_id) ON DELETE CASCADE",
}
CITIES_COLUMN_TYPES = {
    'geonames_id': 'INTEGER NOT NULL UNIQUE PRIMARY KEY',
    'name': 'TEXT NOT NULL',
    'ascii_name': 'TEXT NOT NULL',
    'alternate_names': 'TEXT',
    'latitude': 'REAL NOT NULL',
    'longitude': 'REAL NOT NULL',
    'feature_class': 'TEXT NOT NULL',
    'feature_code': 'TEXT',
    'country_code': 'TEXT NOT NULL',
    'cc2': 'TEXT',
    'admin1_code': 'TEXT',
    'admin2_code': 'TEXT',
    'admin3_code': 'TEXT',
    'admin4_code': 'TEXT',
    'population': 'INTEGER NOT NULL',
    'elevation': 'INTEGER',
    'dem': 'INTEGER NOT NULL',
    'timezone': 'TEXT NOT NULL',
    'modification': 'DATE',
    'administrative_unit_id': f'INTEGER REFERENCES {ADMINISTRATIVE_TABLE_NAME}(geonames_id) ON DELETE CASCADE',
    'country_id': f'INTEGER NOT NULL REFERENCES {COUNTRY_TABLE_NAME}(geonames_id)  ON DELETE CASCADE',
}
COUNTRIES_COLUMN_TYPES = {
    'iso': 'TEXT NOT NULL UNIQUE',
    'iso3': 'TEXT NOT NULL UNIQUE',
    'iso_numeric': 'TEXT NOT NULL UNIQUE',
    'fips': 'TEXT',
    'name': 'TEXT NOT NULL UNIQUE',
    'capital': 'TEXT',
    'area_sq_km': 'REAL NOT NULL',
    'population': 'INTEGER NOT NULL',
    'continent': 'TEXT NOT NULL',
    'tld': 'TEXT',
    'currency_code': 'TEXT',
    'currency_name': 'TEXT',
    'phone': 'TEXT',
    'postal_code_format': 'TEXT',
    'postal_code_regex': 'TEXT',
    'languages': 'TEXT',
    'geonames_id': 'INTEGER NOT NULL UNIQUE PRIMARY KEY',
    'neighbours': 'TEXT',
    'equivalent_fips_code': 'TEXT'
}
ALTERNATE_NAME_COLUMN_TYPES = {
    "id": "INTEGER PRIMARY KEY",
    "geonames_id": "INTEGER NOT NULL",
    "lang": "TEXT",
    "name": "TEXT",
    "is_preferred": "INTEGER",
    "is_short": "INTEGER",
    "is_colloquial": "INTEGER",
    "is_historic": "INTEGER",
    "'from'": "TEXT",
    "'to'": "TEXT",
}


CITY_SELECT_FIELDS = {
    "id": f"{CITY_TABLE_NAME}.geonames_id AS id",
    "geonames_id": f"{CITY_TABLE_NAME}.geonames_id AS geonames_id",
    "name": f"COALESCE({CITY_TABLE_NAME}.name{{0}}, {CITY_TABLE_NAME}.name) AS name",
    "administrative_name": f"COALESCE({ADMINISTRATIVE_TABLE_NAME}.name{{0}}, {ADMINISTRATIVE_TABLE_NAME}.name) AS administrative_name",
    "country_name": f"COALESCE({COUNTRY_TABLE_NAME}.name{{0}}, {COUNTRY_TABLE_NAME}.name) AS country_name",
    "longitude": f"{CITY_TABLE_NAME}.longitude AS longitude",
    "latitude": f"{CITY_TABLE_NAME}.latitude AS latitude",
    "population": f"{CITY_TABLE_NAME}.population AS population",
    "timezone": f"{CITY_TABLE_NAME}.timezone as timezone",
    'ascii_name': f"{CITY_TABLE_NAME}.ascii_name AS ascii_name",
    'alternate_names': f"{CITY_TABLE_NAME}.alternate_names AS alternate_names",
    'feature_class': f"{CITY_TABLE_NAME}.feature_class AS feature_class",
    'feature_code': f"{CITY_TABLE_NAME}.feature_code AS feature_code",
    'country_code': f"{CITY_TABLE_NAME}.country_code AS country_code",
    'cc2': f"{CITY_TABLE_NAME}.cc2 AS cc2",
    'admin1_code': f"{CITY_TABLE_NAME}.admin1_code AS admin1_code",
    'admin2_code': f"{CITY_TABLE_NAME}.admin2_code AS admin2_code",
    'admin3_code': f"{CITY_TABLE_NAME}.admin3_code AS admin3_code",
    'admin4_code': f"{CITY_TABLE_NAME}.admin4_code AS admin4_code",
    'elevation': f"{CITY_TABLE_NAME}.elevation AS elevation",
    'dem': f"{CITY_TABLE_NAME}.dem AS dem",
    'modification': f"{CITY_TABLE_NAME}.modification AS modification",
    "*": f"{CITY_TABLE_NAME}.*"
}
CITY_SELECT_TEMPLATE = f"""
SELECT
{{}}
FROM {CITY_TABLE_NAME}
LEFT JOIN {ADMINISTRATIVE_TABLE_NAME} ON {CITY_TABLE_NAME}.administrative_unit_id = {ADMINISTRATIVE_TABLE_NAME}.geonames_id
LEFT JOIN {COUNTRY_TABLE_NAME} ON {CITY_TABLE_NAME}.country_id = {COUNTRY_TABLE_NAME}.geonames_id 
"""

FTS_CITY_SEARCH_SELECT = CITY_SELECT_TEMPLATE + f"""
INNER JOIN {CITY_FTS_TABLE_NAME} ON {CITY_TABLE_NAME}.geonames_id = {CITY_FTS_TABLE_NAME}.geonames_id
WHERE {CITY_FTS_TABLE_NAME}.name MATCH ? || '*' LIMIT ?;
"""
CITY_SELECT_BY_ID = CITY_SELECT_TEMPLATE + f"""WHERE {CITY_TABLE_NAME}.geonames_id = ?"""
CITY_SELECT_NEAREST = CITY_SELECT_TEMPLATE + f"""
ORDER BY DISTANCE(?, ?, {CITY_TABLE_NAME}.latitude, {CITY_TABLE_NAME}.longitude) 
LIMIT ?
"""


CITY_ALL_FIELDS = tuple(CITY_SELECT_FIELDS.keys())
CITY_MIN_FIELDS = ("id", "name", "administrative_name", "country_name")


