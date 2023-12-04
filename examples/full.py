from dataclasses import dataclass
from pycities import RowFactoryModelConfig, CityDatabase, dict_factory


# You can define your own custom model or use existed ones for: tuple, dict, list, sqlite3.Row
@dataclass(frozen=True)
class City:
    id: int
    name: str
    administrative_name: str
    country_name: str
    longitude: str
    latitude: str


# Create row factory for your custom model
def city_factory(cursor, row) -> City:
    return City(**dict_factory(cursor, row))


# Set your factory config for your custom model
RowFactoryModelConfig.set(City, city_factory)

# Create new instance with our model.
# You can define fields that you want to fetch in SELECT queries.
# All supported fields can be found in `pycities.config.CITY_ALL_FIELDS`
db = CityDatabase[City](
    fetch_fields=("id", "name", "administrative_name", "country_name", "longitude", "latitude")
)
# Connect to datasource
db.connect()
print(db.supported_languages)
# >>> ('uk', 'pl', 'en', 'ru')

print(db.search(query="Wroclaw", lang="pl", limit=1))
# >>> [City(id=3081368, name='Wrocław', administrative_name='Województwo dolnośląskie', country_name='Polska', longitude=17.03333, latitude=51.1)]

for lang in db.supported_languages:
    print(db.get_city(5128581, lang=lang))
# >>> City(id=5128581, name='Нью-Йорк', administrative_name='Нью-Йорк', country_name='США', longitude=-74.00597, latitude=40.71427)
# >>> City(id=5128581, name='Nowy Jork', administrative_name='Nowy Jork', country_name='USA', longitude=-74.00597, latitude=40.71427)
# >>> City(id=5128581, name='New York', administrative_name='New York', country_name='United States', longitude=-74.00597, latitude=40.71427)
# >>> City(id=5128581, name='Нью-Йорк', administrative_name='Нью-Йорк', country_name='США', longitude=-74.00597, latitude=40.71427)

for city in db.get_nearest(latitude=43.313, longitude=-31.123, limit=3):
    print(city)
# >>> City(id=6941014, name='Ponta Delgada', administrative_name='Azores', country_name='Portugal', longitude=-25.66874, latitude=37.73952)
# >>> City(id=2270380, name='Câmara de Lobos', administrative_name='Madeira', country_name='Portugal', longitude=-16.97718, latitude=32.65043)
# >>> City(id=2267827, name='Funchal', administrative_name='Madeira', country_name='Portugal', longitude=-16.92547, latitude=32.66568)

db.close()
