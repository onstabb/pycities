import pytest

from pycities import utils


@pytest.mark.parametrize(
    "point_1, point_2, expected_distance",
    [
        ((32.041, -5.3442), (32.041, -5.3442), 0),
        ((23.03, 33.3213), (21.03, 1.3213), 3299)
    ]

)
def test_calculate_distance(point_1, point_2, expected_distance):
    distance = utils.calculate_distance(*point_1, *point_2)
    assert int(distance) == expected_distance
