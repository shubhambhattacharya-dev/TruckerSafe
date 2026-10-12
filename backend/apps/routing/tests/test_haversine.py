import pytest

from apps.routing.services.geo.haversine import haversine_distance


def test_same_coordinate_returns_zero():
    distance = haversine_distance(
        22.3072, 73.1812,
        22.3072, 73.1812,
    )

    assert distance == 0.0


def test_distance_is_symmetric():
    distance_ab = haversine_distance(
        37.7749, -122.4194,
        34.0522, -118.2437,
    )

    distance_ba = haversine_distance(
        34.0522, -118.2437,
        37.7749, -122.4194,
    )

    assert distance_ab == pytest.approx(distance_ba)


def test_san_francisco_to_los_angeles_distance():
    distance = haversine_distance(
        37.7749, -122.4194,
        34.0522, -118.2437,
    )

    assert 340 < distance < 360


def test_distance_is_non_negative():
    distance = haversine_distance(
        22.3072, 73.1812,
        19.0760, 72.8777,
    )

    assert distance >= 0