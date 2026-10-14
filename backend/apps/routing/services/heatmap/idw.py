"""Inverse-distance weighting (IDW) interpolation for TruckerSafe heatmaps."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

DEFAULT_CHUNK_CELLS = 1 << 16  # 65,536 cells per chunk


def idw_interpolate(
    sample_points: Sequence[tuple[float, float]],
    sample_values: Sequence[float],
    grid_latitudes: np.ndarray,
    grid_longitudes: np.ndarray,
    *,
    power: float = 2.0,
    exact_tolerance: float = 1e-12,
    k: int | None = None,
    chunk_size: int = DEFAULT_CHUNK_CELLS,
) -> np.ndarray:
    """Interpolate sample values onto a 2D latitude/longitude grid.

    Args:
        sample_points: Sample coordinates as (latitude, longitude).
        sample_values: Numeric value associated with each sample.
        grid_latitudes: 2D array containing grid-cell latitudes.
        grid_longitudes: 2D array containing grid-cell longitudes.
        power: Positive finite exponent for inverse-distance weighting.
        exact_tolerance: Non-negative distance tolerance for exact matches,
            measured in latitude/longitude degrees.
        k: Optional number of nearest samples used per grid cell.
        chunk_size: Maximum number of grid cells processed per chunk.

    Returns:
        A 2D NumPy array of interpolated values. Invalid grid cells and
        cells without usable samples contain NaN.

    Notes:
        Distances use Euclidean latitude/longitude degrees. This is an
        approximation for local visualization, not geodesic measurement.
        Invalid samples are discarded. If k is set, interpolation uses
        only the k nearest usable samples.
    """
    if not math.isfinite(power) or power <= 0:
        raise ValueError("power must be finite and greater than zero.")

    if not math.isfinite(exact_tolerance) or exact_tolerance < 0:
        raise ValueError(
            "exact_tolerance must be finite and non-negative."
        )

    if k is not None and (
        isinstance(k, bool) or not isinstance(k, int) or k < 1
    ):
        raise ValueError("k must be a positive integer or None.")

    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
        raise ValueError("chunk_size must be a positive integer.")

    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1.")

    points, values = _prepare_samples(sample_points, sample_values)

    lat_grid = np.asarray(grid_latitudes, dtype=float)
    lon_grid = np.asarray(grid_longitudes, dtype=float)

    if lat_grid.shape != lon_grid.shape:
        raise ValueError(
            "grid_latitudes and grid_longitudes must have the same shape."
        )

    if lat_grid.ndim != 2:
        raise ValueError(
            "Grid latitude and longitude arrays must be two-dimensional."
        )

    result = np.full(lat_grid.shape, np.nan, dtype=float)

    if len(points) == 0:
        return result

    usable_cells = np.isfinite(lat_grid) & np.isfinite(lon_grid)
    if not usable_cells.any():
        return result

    grid_coordinates = np.column_stack(
        (lat_grid[usable_cells], lon_grid[usable_cells])
    )

    interpolated = np.empty(len(grid_coordinates), dtype=float)

    for start in range(0, len(grid_coordinates), chunk_size):
        end = min(start + chunk_size, len(grid_coordinates))

        interpolated[start:end] = _interpolate_chunk(
            grid_coordinates[start:end],
            points,
            values,
            power=power,
            exact_tolerance=exact_tolerance,
            k=k,
        )

    result[usable_cells] = interpolated
    return result


def _prepare_samples(
    sample_points: Sequence[tuple[float, float]],
    sample_values: Sequence[float],
) -> tuple[np.ndarray, np.ndarray]:
    """Validate sample shapes and discard unusable samples."""
    if len(sample_points) != len(sample_values):
        raise ValueError(
            "sample_points and sample_values must have equal lengths."
        )

    if len(sample_points) == 0:
        return np.empty((0, 2), dtype=float), np.empty(0, dtype=float)

    points = np.asarray(sample_points, dtype=float)
    values = np.asarray(sample_values, dtype=float)

    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError(
            "Each sample point must contain latitude and longitude."
        )

    if values.ndim != 1:
        raise ValueError("sample_values must be one-dimensional.")

    valid = (
        np.isfinite(points).all(axis=1)
        & np.isfinite(values)
        & (np.abs(points[:, 0]) <= 90)
        & (np.abs(points[:, 1]) <= 180)
    )

    return points[valid], values[valid]


def _interpolate_chunk(
    grid_coords: np.ndarray,
    points: np.ndarray,
    values: np.ndarray,
    *,
    power: float,
    exact_tolerance: float,
    k: int | None,
) -> np.ndarray:
    """Interpolate one chunk of grid cells."""
    differences = grid_coords[:, np.newaxis, :] - points[np.newaxis, :, :]
    distances = np.sqrt(np.einsum("mni,mni->mn", differences, differences))

    if k is not None and k < distances.shape[1]:
        nearest_indices = np.argpartition(
            distances, kth=k - 1, axis=1
        )[:, :k]

        distances = np.take_along_axis(distances, nearest_indices, axis=1)
        selected_values = values[nearest_indices]
    else:
        selected_values = np.broadcast_to(values, distances.shape)

    exact_matches = distances <= exact_tolerance
    has_exact = exact_matches.any(axis=1)

    output = np.empty(len(grid_coords), dtype=float)

    if has_exact.any():
        matches = exact_matches[has_exact]
        matching_values = selected_values[has_exact]

        counts = matches.sum(axis=1)
        sums = np.sum(
            np.where(matches, matching_values, 0.0),
            axis=1,
        )
        output[has_exact] = sums / counts

    non_exact = ~has_exact

    if non_exact.any():
        d = distances[non_exact]
        v = selected_values[non_exact]

        # Normalize by the smallest distance in each row to avoid
        # unnecessary overflow from directly calculating 1 / d**power.
        min_distances = d.min(axis=1, keepdims=True)
        relative_distances = d / min_distances

        with np.errstate(over="ignore", under="ignore", divide="ignore"):
            weights = np.power(relative_distances, -power)

        weight_sums = weights.sum(axis=1)
        weighted_sums = np.sum(weights * v, axis=1)

        output[non_exact] = weighted_sums / weight_sums

    return output
