import pytest

import database
import model


@pytest.fixture(scope="module")
def city_db(data_dir):
    cities = database.CityDatabase[model.CityInfo](fetch_fields=("id", "name", "administrative_name", "country_name"))
    cities.connect(data_dir / "data.db")
    yield cities
    cities.close()


def test_supported_languages(city_db, languages):
    assert city_db.supported_languages == tuple(languages)


@pytest.mark.parametrize(
    "city_id, lang, expected_name",
    [
        (3081368, "en", "Wroclaw"),
        (703448, "uk", "Київ")
    ]
)
def test_get_city(city_db, city_id, lang, expected_name):
    city = city_db.get_city(city_id, lang=lang)
    assert city
    assert city.name == expected_name


@pytest.mark.parametrize(
    "query, expected_length",
    [
        ("query", 0),
        ("Kyiv", 1),
        ("Bre", 64)
    ]
)
def test_search_city(city_db, query, expected_length):
    cities = city_db.search(query)
    assert len(cities) == expected_length


@pytest.mark.parametrize(
    "point, expected_city_ids",
    [
        ([51.1, 17.03333], (3081368, 12047628, 12047644)),
    ]
)
def test_get_nearest(city_db, point, expected_city_ids):
    cities = city_db.get_nearest(*point, limit=3)
    assert all(city.id == city_id for city, city_id in zip(cities, expected_city_ids))


@pytest.mark.parametrize(
    "row_cls, row_factory",
    [
        (tuple, lambda cur, row: row),
        (list, lambda cur, row: list(row))
    ]

)
def test_row_factory_config(data_dir, row_cls, row_factory):
    model.RowFactoryModelConfig.set(row_cls, row_factory)
    db = database.CityDatabase[row_cls]().connect(data_dir / "data.db")

    city = db.get_city(3081368, lang="")
    assert city
    assert isinstance(city, row_cls)

    db.close()
