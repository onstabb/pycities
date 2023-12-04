import math


def calculate_distance(lat_1: float, long_1: float, lat_2: float, long_2: float) -> float:
    """
    Calculate the great circle distance between two points on the
    earth using Haversine formula. It returns the distance in
    kilometers.

    :param lat_1: latitude of first point
    :param long_1: longitude of first point
    :param lat_2: latitude of second point
    :param long_2: longitude of second point
    :return: distance in kilometers between the two sets of coordinates
    """

    if (lat_1, long_1) == (lat_2, long_2):
        return 0.0

    lat_1, long_1, lat_2, long_2 = math.radians(lat_1), math.radians(long_1), math.radians(lat_2), math.radians(long_2)
    d_lat, d_long = lat_2 - lat_1, long_2 - long_1
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat_1) * math.cos(lat_2) * math.sin(d_long / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r_km = 6371
    return c * r_km
