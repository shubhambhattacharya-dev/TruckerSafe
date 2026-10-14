"""Tests for the TruckerSafe IDW heatmap helper."""

import numpy as np
import pytest

from apps.routing.services.heatmap.idw import idw_interpolate


def test_exact_location_returns_sample_value():
    result = idw_interpolate(
        [(0.0, 0.0)],
        [12.0],
        np.array([[0.0]]),
        np.array([[0.0]]),
    )

    assert result[0, 0] == pytest.approx(12.0)


def test_equal_distance_returns_average():
    result = idw_interpolate(
        [(0.0, 0.0), (0.0, 1.0)],
        [10.0, 20.0],
        np.array([[0.0]]),
        np.array([[0.5]]),
    )

    assert result[0, 0] == pytest.approx(15.0)


def test_closer_sample_has_more_influence():
    result = idw_interpolate(
        [(0.0, 0.0), (0.0, 1.0)],
        [10.0, 30.0],
        np.array([[0.0]]),
        np.array([[0.25]]),
    )

    assert result[0, 0] < 20.0


def test_no_samples_returns_unknown_value():
    result = idw_interpolate(
        [],
        [],
        np.array([[0.0]]),
        np.array([[0.0]]),
    )

    assert np.isnan(result[0, 0])


def test_invalid_grid_cell_returns_unknown_value():
    result = idw_interpolate(
        [(0.0, 0.0)],
        [10.0],
        np.array([[np.nan]]),
        np.array([[0.0]]),
    )

    assert np.isnan(result[0, 0])


@pytest.mark.parametrize(
    ("power", "k", "chunk_size"),
    [
        (0.0, None, 10),
        (float("nan"), None, 10),
        (2.0, 0, 10),
        (2.0, None, 0),
    ],
)
def test_invalid_settings_are_rejected(power, k, chunk_size):
    with pytest.raises(ValueError):
        idw_interpolate(
            [(0.0, 0.0)],
            [10.0],
            np.array([[0.0]]),
            np.array([[0.0]]),
            power=power,
            k=k,
            chunk_size=chunk_size,
        )


def test_nearest_sample_option_returns_finite_value():
    result = idw_interpolate(
        [(0.0, 0.0), (0.0, 1.0), (0.0, 2.0)],
        [10.0, 20.0, 30.0],
        np.array([[0.0]]),
        np.array([[0.4]]),
        k=1,
    )

    assert result[0, 0] == pytest.approx(10.0)


def test_chunked_and_unchunked_results_match():
    latitudes = np.array([[0.0, 0.0], [0.0, 0.0]])
    longitudes = np.array([[0.2, 0.5], [0.8, 1.0]])
    points = [(0.0, 0.0), (0.0, 1.0)]
    values = [10.0, 20.0]

    whole = idw_interpolate(
        points, values, latitudes, longitudes, chunk_size=100
    )
    chunks = idw_interpolate(
        points, values, latitudes, longitudes, chunk_size=1
    )

    np.testing.assert_allclose(whole, chunks)
