"""Build wind, rain, and snow heatmap grids along a truck route."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, TypedDict

import numpy as np

from apps.routing.services.heatmap.idw import idw_interpolate

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GRID_SPACING_DEGREES = 0.08
BBOX_BUFFER_DEGREES = 1.0

#: Corridor half-width from the guidebook, in kilometres.
MAX_ROUTE_DISTANCE_KM = 150.0
KM_PER_MILE = 1.609344
#: Same corridor, expressed in miles so it can be compared against the
#: miles-valued haversine distance below.
MAX_ROUTE_DISTANCE_MILES = MAX_ROUTE_DISTANCE_KM / KM_PER_MILE

NEAREST_SAMPLES = 8
ROUND_DIGITS = 4

#: Mean Earth radius in miles. Must match ``haversine_distance``.
EARTH_RADIUS_MILES = 3958.7613

WeatherLayer = Literal["wind", "rain", "snow"]


class WeatherSample(TypedDict):
    latitude: float
    longitude: float
    wind: float | None
    rain: float | None
    snow: float | None


class Heatmap(TypedDict):
    bbox: list[float]
    rows: int
    cols: int
    wind: list[float | None]
    rain: list[float | None]
    snow: list[float | None]


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------
def _as_route_array(
    route_points: Sequence[tuple[float, float]],
) -> np.ndarray:
    """Normalise route points to a float ``(N, 2)`` array of (lat, lon)."""
    array = np.asarray(route_points, dtype=float)
    if array.size == 0:
        raise ValueError("Route must contain at least one point.")
    if array.ndim != 2 or array.shape[1] != 2:
        raise ValueError(
            "route_points must be a sequence of (latitude, longitude) pairs."
        )
    if not np.isfinite(array).all():
        raise ValueError("Route coordinates must be finite numbers.")
    if not ((-90.0 <= array[:, 0]) & (array[:, 0] <= 90.0)).all():
        raise ValueError("Route latitudes must be between -90 and 90 degrees.")
    if not ((-180.0 <= array[:, 1]) & (array[:, 1] <= 180.0)).all():
        raise ValueError("Route longitudes must be between -180 and 180 degrees.")
    return array


def _build_bbox(route_array: np.ndarray) -> list[float]:
    """Return [west, south, east, north] with a 1-degree buffer, clamped to geographic limits."""
    latitudes = route_array[:, 0]
    longitudes = route_array[:, 1]
    return [
        float(max(-180.0, longitudes.min() - BBOX_BUFFER_DEGREES)),
        float(max(-90.0, latitudes.min() - BBOX_BUFFER_DEGREES)),
        float(min(180.0, longitudes.max() + BBOX_BUFFER_DEGREES)),
        float(min(90.0, latitudes.max() + BBOX_BUFFER_DEGREES)),
    ]


def _densify_route(route_array: np.ndarray, max_step_miles: float = 10.0) -> np.ndarray:
    """Ensure consecutive points along the route are no more than max_step_miles apart."""
    if len(route_array) <= 1:
        return route_array

    dense_points: list[np.ndarray] = [route_array[0]]
    for p1, p2 in zip(route_array, route_array[1:]):
        # 1 deg latitude is approx 69 miles
        dlat = (p2[0] - p1[0]) * 69.0
        avg_lat = np.radians((p1[0] + p2[0]) / 2.0)
        dlon = (p2[1] - p1[1]) * 69.0 * np.cos(avg_lat)
        approx_dist_mi = float(np.hypot(dlat, dlon))

        if approx_dist_mi > max_step_miles:
            steps = int(np.ceil(approx_dist_mi / max_step_miles))
            for s in range(1, steps):
                frac = s / steps
                dense_points.append(p1 + frac * (p2 - p1))
        dense_points.append(p2)

    return np.asarray(dense_points, dtype=float)


def _haversine_miles(
    grid_lat: np.ndarray,
    grid_lon: np.ndarray,
    point_lat: float,
    point_lon: float,
) -> np.ndarray:
    """Vectorised haversine distance (miles) from a scalar point to a grid.

    Semantics must match ``apps.routing.services.geo.haversine``; only the
    radius and units are duplicated here to allow array evaluation.
    """
    phi1 = np.radians(grid_lat)
    phi2 = np.radians(point_lat)
    dphi = np.radians(point_lat - grid_lat)
    dlambda = np.radians(point_lon - grid_lon)

    a = (
        np.sin(dphi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0) ** 2
    )
    # Clip guards against tiny FP overshoots that would produce NaN.
    return 2.0 * EARTH_RADIUS_MILES * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def _min_distance_to_route_miles(
    grid_latitudes: np.ndarray,
    grid_longitudes: np.ndarray,
    route_array: np.ndarray,
) -> np.ndarray:
    """Minimum haversine distance from each grid cell to any densified route segment."""
    dense_route = _densify_route(route_array, max_step_miles=8.0)
    min_distance = np.full(grid_latitudes.shape, np.inf, dtype=float)
    for lat, lon in dense_route:
        np.minimum(
            min_distance,
            _haversine_miles(grid_latitudes, grid_longitudes, lat, lon),
            out=min_distance,
        )
    return min_distance


# ---------------------------------------------------------------------------
# Interpolation helpers
# ---------------------------------------------------------------------------
def _interpolate_layer(
    layer: WeatherLayer,
    samples: Sequence[WeatherSample],
    grid_latitudes: np.ndarray,
    grid_longitudes: np.ndarray,
) -> np.ndarray:
    """IDW-interpolate one weather layer onto the grid.

    Missing measurements stay missing (NaN), never zero.
    """
    points: list[tuple[float, float]] = []
    values: list[float] = []

    for sample in samples:
        value = sample[layer]
        if value is None or not np.isfinite(value):
            continue
        points.append((sample["latitude"], sample["longitude"]))
        values.append(float(value))

    if not points:
        return np.full(grid_latitudes.shape, np.nan, dtype=float)

    return idw_interpolate(
        points,
        values,
        grid_latitudes,
        grid_longitudes,
        power=2.0,
        k=NEAREST_SAMPLES,
    )


def _serialize(grid: np.ndarray) -> list[float | None]:
    """Flatten a grid to JSON-friendly values, preserving NaN as None."""
    flat = np.round(grid, ROUND_DIGITS).ravel()
    return [None if not np.isfinite(v) else float(v) for v in flat]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def build_heatmap(
    route_points: Sequence[tuple[float, float]],
    weather_samples: Sequence[WeatherSample],
) -> Heatmap:
    """Build wind, rain, and snow grids for a route at one forecast time.

    Args:
        route_points: Route vertices as (latitude, longitude) pairs.
        weather_samples: Per-station readings. Any layer whose value is
            ``None`` or non-finite is excluded from that layer's grid;
            it is **not** treated as zero.

    Returns:
        A :class:`Heatmap` with flat row-major grids and NaN represented
        as ``None``.
    """
    route_array = _as_route_array(route_points)
    bbox = _build_bbox(route_array)
    west, south, east, north = bbox

    rows = max(2, int(np.ceil((north - south) / GRID_SPACING_DEGREES)) + 1)
    cols = max(2, int(np.ceil((east - west) / GRID_SPACING_DEGREES)) + 1)

    latitudes = np.linspace(south, north, rows)
    longitudes = np.linspace(west, east, cols)
    grid_latitudes, grid_longitudes = np.meshgrid(
        latitudes, longitudes, indexing="ij"
    )

    wind_grid = _interpolate_layer(
        "wind", weather_samples, grid_latitudes, grid_longitudes
    )
    rain_grid = _interpolate_layer(
        "rain", weather_samples, grid_latitudes, grid_longitudes
    )
    snow_grid = _interpolate_layer(
        "snow", weather_samples, grid_latitudes, grid_longitudes
    )

    # Mask cells outside the corridor. Vectorised: one pass per route vertex
    # rather than one pass per grid cell.
    distances = _min_distance_to_route_miles(
        grid_latitudes, grid_longitudes, route_array
    )
    outside = distances > MAX_ROUTE_DISTANCE_MILES
    if outside.any():
        wind_grid[outside] = np.nan
        rain_grid[outside] = np.nan
        snow_grid[outside] = np.nan

    return {
        "bbox": bbox,
        "rows": rows,
        "cols": cols,
        "wind": _serialize(wind_grid),
        "rain": _serialize(rain_grid),
        "snow": _serialize(snow_grid),
    }