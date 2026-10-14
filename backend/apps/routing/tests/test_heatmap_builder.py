
import numpy as np
import pytest

from apps.routing.services.heatmap.builder import (
    GRID_SPACING_DEGREES,
    MAX_ROUTE_DISTANCE_MILES,
    build_heatmap,
)


@pytest.fixture
def route():
    """A short route near the equator."""
    return [(0.0, 0.0), (0.0, 0.2)]


@pytest.fixture
def samples():
    """Weather samples around the route."""
    return [
        {
            "latitude": 0.0,
            "longitude": 0.0,
            "wind": 20.0,
            "rain": 0.1,
            "snow": 0.0,
        },
        {
            "latitude": 0.0,
            "longitude": 0.2,
            "wind": 40.0,
            "rain": 0.3,
            "snow": 0.2,
        },
        {
            "latitude": 0.1,
            "longitude": 0.1,
            "wind": 30.0,
            "rain": 0.2,
            "snow": 0.1,
        },
    ]


def test_returns_expected_response_fields(route, samples):
    result = build_heatmap(route, samples)

    assert set(result) == {
        "bbox", "rows", "cols", "wind", "rain", "snow"
    }


def test_bbox_has_one_degree_buffer(route, samples):
    result = build_heatmap(route, samples)

    west, south, east, north = result["bbox"]

    assert west == pytest.approx(-1.0)
    assert south == pytest.approx(-1.0)
    assert east == pytest.approx(1.2)
    assert north == pytest.approx(1.0)


def test_grid_dimensions_match_flat_arrays(route, samples):
    result = build_heatmap(route, samples)

    assert result["rows"] >= 2
    assert result["cols"] >= 2

    for layer in ("wind", "rain", "snow"):
        assert len(result[layer]) == result["rows"] * result["cols"]


def test_grid_uses_approximately_expected_spacing(route, samples):
    result = build_heatmap(route, samples)
    west, south, east, north = result["bbox"]

    longitude_spacing = (east - west) / (result["cols"] - 1)
    latitude_spacing = (north - south) / (result["rows"] - 1)

    # linspace fits the grid to the bounding box, so spacing is approximate.
    assert longitude_spacing == pytest.approx(
        GRID_SPACING_DEGREES, abs=0.01
    )
    assert latitude_spacing == pytest.approx(
        GRID_SPACING_DEGREES, abs=0.01
    )


def test_weather_values_are_json_safe(route, samples):
    result = build_heatmap(route, samples)

    for layer in ("wind", "rain", "snow"):
        for value in result[layer]:
            assert value is None or np.isfinite(value)


def test_missing_layer_is_not_treated_as_zero(route):
    samples = [
        {
            "latitude": 0.0,
            "longitude": 0.0,
            "wind": None,
            "rain": None,
            "snow": None,
        }
    ]

    result = build_heatmap(route, samples)

    # No usable samples means no interpolated weather values.
    for layer in ("wind", "rain", "snow"):
        assert all(value is None for value in result[layer])


def test_missing_value_only_affects_its_layer(route):
    samples = [
        {
            "latitude": 0.0,
            "longitude": 0.0,
            "wind": 25.0,
            "rain": None,
            "snow": 0.5,
        }
    ]

    result = build_heatmap(route, samples)

    assert any(value is not None for value in result["wind"])
    assert all(value is None for value in result["rain"])
    assert any(value is not None for value in result["snow"])


def test_empty_route_raises_error(samples):
    with pytest.raises(ValueError, match="Route must contain"):
        build_heatmap([], samples)


def test_invalid_route_shape_raises_error(samples):
    with pytest.raises(ValueError, match="route_points"):
        build_heatmap([(0.0, 0.0, 1.0)], samples)


def test_outside_corridor_cells_are_masked(route, samples):
    result = build_heatmap(route, samples)

    west, south, east, north = result["bbox"]
    latitudes = np.linspace(south, north, result["rows"])
    longitudes = np.linspace(west, east, result["cols"])

    # Select the grid cell at the northwest corner, far from this route.
    row, col = 0, 0
    latitude = latitudes[row]
    longitude = longitudes[col]

    assert abs(latitude) >= 1.0
    assert abs(longitude) >= 1.0

    index = row * result["cols"] + col

    for layer in ("wind", "rain", "snow"):
        assert result[layer][index] is None


def test_nearby_route_cells_are_not_all_masked(route, samples):
    result = build_heatmap(route, samples)

    # There should be usable cells close to the route.
    assert any(value is not None for value in result["wind"])
    assert any(value is not None for value in result["rain"])
    assert any(value is not None for value in result["snow"])


def test_mask_distance_constant_is_approximately_150_km():
    assert MAX_ROUTE_DISTANCE_MILES == pytest.approx(
        150.0 / 1.609344
    )


def test_out_of_range_latitude_raises_error(samples):
    with pytest.raises(ValueError, match="latitudes must be between -90 and 90"):
        build_heatmap([(95.0, 0.0), (0.0, 0.0)], samples)


def test_out_of_range_longitude_raises_error(samples):
    with pytest.raises(ValueError, match="longitudes must be between -180 and 180"):
        build_heatmap([(0.0, 190.0), (0.0, 0.0)], samples)


def test_non_finite_coordinates_raise_error(samples):
    with pytest.raises(ValueError, match="finite numbers"):
        build_heatmap([(float("nan"), 0.0)], samples)

