# -*- coding: utf-8 -*-
import logging
import sqlite3
import sys
from functools import lru_cache
from os import PathLike
from typing import Optional, Generic, Union, Type, Tuple, List

from . import config
from .model import TCityModel, RowFactoryModelConfig
from .utils import calculate_distance


class CityDatabase(Generic[TCityModel]):

    def __init__(self, fetch_fields: Optional[Tuple[str, ...]] = None) -> None:
        self.__conn: Optional[sqlite3.Connection] = None
        self.__cursor: Optional[sqlite3.Cursor] = None
        self._log = logging.getLogger(self.__class__.__name__)
        self.fetch_fields = fetch_fields or ("*", )

    def connect(self, datasource: Union[str, PathLike] = config.DEFAULT_DATA_SOURCE, **params) -> 'CityDatabase':
        """Creates a new connection to the datasource"""

        check_same_thread = params.get("check_same_thread", False)
        self.__conn = sqlite3.connect(datasource, check_same_thread=check_same_thread, **params)

        if sys.version_info >= (3, 8):
            self.__conn.create_function("DISTANCE", 4, calculate_distance, deterministic=True)
        else:
            self.__conn.create_function("DISTANCE", 4, calculate_distance)

        self._log.info('Connected source "%s"', datasource)
        self._log.debug(f"Languages found: %s", ",".join(self.supported_languages))
        return self

    @property
    def supported_languages(self) -> Tuple[str, ...]:
        """Gets a sequence of languages available in the database"""

        result = self.conn.execute(
            "SELECT SUBSTR(name, 6, 2) as languages FROM PRAGMA_TABLE_INFO(?) WHERE name LIKE 'name_' || '%'",
            (config.CITY_TABLE_NAME,)
        )
        return tuple(lang[0] for lang in result)

    @property
    @lru_cache(1)
    def _row_cls(self) -> Type[TCityModel]:
        orig_class = self.__dict__.get("__orig_class__")
        if not orig_class:
            raise ValueError(
                "Generic wasn't provided or an attempt was made to access from __init__ which is not allowed"
            )
        return orig_class.__args__[0]

    @property
    def conn(self) -> sqlite3.Connection:
        if not self.__conn:
            raise RuntimeError("There is no connection to the datasource")
        return self.__conn

    @property
    def cursor(self) -> sqlite3.Cursor:
        if not self.__cursor:
            self.__cursor = self.conn.cursor()
            self.__cursor.row_factory = RowFactoryModelConfig.get(self._row_cls)
        return self.__cursor

    @staticmethod
    @lru_cache(None)
    def _prepare_select_template(field_names: Tuple[str, ...], template_query: str, lang: str = "") -> str:
        fields = (config.CITY_SELECT_FIELDS[field] for field in field_names)
        return template_query.format(",".join(fields)).format(f"_{lang}" if lang else "")

    def search(self, query: str, *, lang: str = "", limit: int = -1) -> List[TCityModel]:
        """
        Searches for cities based on a given query string.
        The search is carried out by the FTS5 module using the “alternate_names” column.

        :param query: Input query string
        :param lang: Names in particular language for some columns
        :param limit: Limit of the result
        :return: List of suitable cities
        """

        select_query = self._prepare_select_template(self.fetch_fields, config.FTS_CITY_SEARCH_SELECT, lang)
        result = self.cursor.execute(select_query, (query, limit))
        return result.fetchall()

    def get_city(self, geonames_id: int, *, lang: str = "") -> Optional[TCityModel]:
        select_query = self._prepare_select_template(self.fetch_fields, config.CITY_SELECT_BY_ID, lang)
        result = self.cursor.execute(select_query, (geonames_id,))
        return result.fetchone()

    def get_nearest(self, latitude: float, longitude: float, *, lang: str = "", limit: int = 1) -> List[TCityModel]:
        """
        Gets nearest cities by given point with latitude and longitude

        :param latitude: Latitude of the point
        :param longitude: Longitude of the point
        :param lang: Names in particular language for some columns
        :param limit: Limit of the result
        :return: List of nearest cities to the given point
        """

        query = self._prepare_select_template(self.fetch_fields, config.CITY_SELECT_NEAREST, lang)
        result = self.cursor.execute(query, (latitude, longitude, limit))
        return result.fetchall()

    def close(self) -> None:
        self.cursor.close()
        self.conn.close()
        self._log.info("Disconnected")
