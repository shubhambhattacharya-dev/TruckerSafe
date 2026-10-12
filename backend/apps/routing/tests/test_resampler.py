
import pytest

from apps.routing.services.geo.resampler import resample_polyline


def test_empty_route():
    assert resample_polyline([]) == []


def test_single_point_route():
    points = [(22.30, 73.18)]

    result = resample_polyline(points)

    assert result == points


def test_short_route_keeps_destination():
    # Route is shorter than the default 25-mile interval.
    points = [
        (22.30, 73.18),
        (22.31, 73.18),
    ]

    result = resample_polyline(points)

    assert result[0] == points[0]
    assert result[-1] == points[-1]


def test_route_keeps_start_and_destination():
    points = [
        (22.30, 73.18),
        (22.40, 73.25),
        (22.50, 73.40),
    ]

    result = resample_polyline(points)

    assert result[0] == points[0]
    assert result[-1] == points[-1]


def test_duplicate_consecutive_points():
    points = [
        (22.30, 73.18),
        (22.30, 73.18),
        (22.40, 73.25),
    ]

    result = resample_polyline(points)

    assert result[0] == points[0]
    assert result[-1] == points[-1]


@pytest.mark.parametrize("interval", [10, 25, 50])
def test_accepts_valid_intervals(interval):
    points = [
        (22.30, 73.18),
        (22.40, 73.25),
        (22.50, 73.40),
    ]

    result = resample_polyline(points, interval_miles=interval)

    assert result[0] == points[0]
    assert result[-1] == points[-1]
    assert len(result) >= 2


@pytest.mark.parametrize("interval", [0, -1, float("inf"), float("-inf"), float("nan"), True, False, "25", None])
def test_rejects_invalid_intervals(interval):
    with pytest.raises(ValueError):
        resample_polyline(
            [(22.30, 73.18), (22.40, 73.25)],
            interval_miles=interval,
        )


@pytest.mark.parametrize(
    "points",
    [
        [(91, 0), (22, 73)],       # Latitude too high
        [(-91, 0), (22, 73)],      # Latitude too low
        [(22, 181), (22, 73)],     # Longitude too high
        [(22, -181), (22, 73)],    # Longitude too low
        [(float("nan"), 73), (22, 73)],
        [(float("inf"), 73), (22, 73)],
        [(22,)],                   # Wrong coordinate shape
    ],
)
def test_rejects_invalid_coordinates(points):
    with pytest.raises(ValueError):
        resample_polyline(points)
