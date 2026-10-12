
import pytest

from apps.routing.services.geo.simplify import simplify_polyline


def test_empty_route():
    assert simplify_polyline([]) == []


def test_single_point_route():
    points = [(22.30, 73.18)]

    assert simplify_polyline(points) == points


def test_two_point_route_preserves_endpoints():
    points = [
        (22.30, 73.18),
        (22.50, 73.40),
    ]

    assert simplify_polyline(points) == points


def test_straight_route_removes_intermediate_points():
    points = [
        (22.30, 73.18),
        (22.31, 73.19),
        (22.32, 73.20),
        (22.33, 73.21),
    ]

    result = simplify_polyline(points, tolerance_miles=0.1)

    assert result[0] == points[0]
    assert result[-1] == points[-1]
    assert len(result) == 2


def test_curved_route_preserves_important_bend():
    points = [
        (22.30, 73.18),
        (22.31, 73.18),
        (22.32, 73.25),
        (22.33, 73.18),
    ]

    result = simplify_polyline(points, tolerance_miles=0.1)

    assert result[0] == points[0]
    assert result[-1] == points[-1]
    assert len(result) > 2


def test_zero_tolerance_preserves_all_points():
    points = [
        (22.30, 73.18),
        (22.31, 73.19),
        (22.32, 73.20),
    ]

    result = simplify_polyline(points, tolerance_miles=0)

    assert result == points


def test_large_tolerance_keeps_endpoints():
    points = [
        (22.30, 73.18),
        (22.31, 73.19),
        (22.32, 73.20),
    ]

    result = simplify_polyline(points, tolerance_miles=100)

    assert result == [points[0], points[-1]]


@pytest.mark.parametrize(
    "tolerance",
    [-1, float("inf"), float("-inf"), float("nan"), True, False, "0.1", None],
)
def test_invalid_tolerance_raises_value_error(tolerance):
    with pytest.raises(ValueError):
        simplify_polyline(
            [(22.30, 73.18), (22.40, 73.25)],
            tolerance_miles=tolerance,
        )


@pytest.mark.parametrize(
    "points",
    [
        [(91, 0), (22, 73)],
        [(-91, 0), (22, 73)],
        [(22, 181), (22, 73)],
        [(22, -181), (22, 73)],
        [(float("nan"), 73), (22, 73)],
        [(float("inf"), 73), (22, 73)],
        [(22,)],
        [(True, 73), (22, 73)],
        [("22", 73), (22, 73)],
    ],
)
def test_invalid_coordinates_raise_value_error(points):
    with pytest.raises(ValueError):
        simplify_polyline(points)


def test_antimeridian_route_preserves_endpoints():
    points = [
        (10.0, 179.8),
        (10.1, 179.9),
        (10.2, -179.9),
    ]

    result = simplify_polyline(points, tolerance_miles=0.1)

    assert result[0] == points[0]
    assert result[-1] == points[-1]


def test_input_sequence_is_not_modified():
    points = [
        (22.30, 73.18),
        (22.31, 73.19),
        (22.32, 73.20),
    ]
    original = points.copy()

    simplify_polyline(points)

    assert points == original
