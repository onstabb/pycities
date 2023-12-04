import sqlite3
from dataclasses import dataclass
from sqlite3 import Cursor, Row
from typing import TypeVar, Callable, Dict


TCityModel = TypeVar("TCityModel")
RowFactory = Callable[[sqlite3.Cursor, tuple], TCityModel]


@dataclass(frozen=True  )
class CityInfo:
    id: int
    name: str
    administrative_name: str
    country_name: str


def tuple_factory(_cursor: Cursor, row: tuple) -> tuple:
    return row


def list_factory(_cursor, row: tuple) -> list:
    return list(row)


def dict_factory(cursor: Cursor, row: tuple) -> dict:
    return {desc[0]: row[i] for i, desc in enumerate(cursor.description)}


class RowFactoryModelConfig:

    _row_factories: Dict[type, RowFactory] = {
        tuple: tuple_factory,
        dict: dict_factory,
        Row: Row,
        CityInfo: lambda _cursor, row: CityInfo(*row),
    }

    @classmethod
    def set(cls, row_cls: type, row_factory: RowFactory) -> None:
        cls._row_factories[row_cls] = row_factory

    @classmethod
    def get(cls, row_cls: type) -> RowFactory:
        row_factory = cls._row_factories.get(row_cls)
        if not row_factory:
            raise ValueError(f"Factory for {row_cls} does not exists")

        return row_factory
