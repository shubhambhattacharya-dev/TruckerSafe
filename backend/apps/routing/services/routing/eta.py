
"""Estimate checkpoint arrival times along a route."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from numbers import Real
from typing import Final, NamedTuple, Sequence, TypedDict

from apps.routing.services.geo.haversine import haversine_distance
from apps.routing.services.routing.base import (
    RouteDict,
    RoutingInputError,
)

__all__ = [
    "CheckpointETA",
    "RouteProjector",
    "estimate_checkpoint_etas",
]

METERS_PER_MILE: Final = 1609.344
ORDER_TOLERANCE_MILES: Final = 1e-6

# Checkpoints farther from the route are rejected by default.
DEFAULT_MAX_CHECKPOINT_OFFSET_MILES: Final = 1.0

# Used to detect clearly inconsistent route data, not to assert that
# road distance and geometry-derived great-circle distance are identical.
DISTANCE_MISMATCH_REL_TOL: Final = 0.10
DISTANCE_MISMATCH_ABS_TOL_MILES: Final = 5.0


class CheckpointETA(TypedDict):
    """Estimated arrival time and cumulative distance for a checkpoint."""

    distance_miles: float
    arrival_time: datetime


class _Projection(NamedTuple):
    distance_miles: float
    offset_miles: float


def _validate_number(value: object, name: str) -> float:
    """Validate a finite, non-negative numeric value."""
    if (
        isinstance(value, bool)
        or not isinstance(value, Real)
        or not math.isfinite(value)
        or value < 0
    ):
        raise RoutingInputError(
            f"{name} must be a finite, non-negative number."
        )

    return float(value)


def _normalize_departure_time(departure_time: datetime) -> datetime:
    """Require a timezone-aware datetime and normalize it to UTC."""
    if not isinstance(departure_time, datetime):
        raise RoutingInputError("departure_time must be a datetime.")

    if (
        departure_time.tzinfo is None
        or departure_time.utcoffset() is None
    ):
        raise RoutingInputError(
            "departure_time must include a timezone."
        )

    return departure_time.astimezone(timezone.utc)


def _validate_geometry(
    geometry: object,
) -> list[tuple[float, float]]:
    """Validate geometry vertices stored as [longitude, latitude]."""
    if not isinstance(geometry, (list, tuple)) or len(geometry) < 2:
        raise RoutingInputError(
            "Route geometry must contain at least two vertices."
        )

    vertices: list[tuple[float, float]] = []

    for index, vertex in enumerate(geometry):
        if not isinstance(vertex, (list, tuple)) or len(vertex) < 2:
            raise RoutingInputError(
                f"Geometry vertex {index} must contain longitude "
                "and latitude."
            )

        lon, lat = vertex[0], vertex[1]

        if (
            isinstance(lon, bool)
            or isinstance(lat, bool)
            or not isinstance(lon, Real)
            or not isinstance(lat, Real)
        ):
            raise RoutingInputError(
                f"Geometry vertex {index} must contain numeric coordinates."
            )

        lon, lat = float(lon), float(lat)

        if not math.isfinite(lon) or not math.isfinite(lat):
            raise RoutingInputError(
                f"Geometry vertex {index} must contain finite coordinates."
            )

        if not -180 <= lon <= 180 or not -90 <= lat <= 90:
            raise RoutingInputError(
                f"Geometry vertex {index} is outside geographic bounds."
            )

        vertices.append((lon, lat))

    return vertices


def _validate_checkpoint(
    checkpoint: object,
    index: int,
) -> tuple[float, float]:
    """Validate one checkpoint expressed as (latitude, longitude)."""
    if (
        not isinstance(checkpoint, (tuple, list))
        or len(checkpoint) != 2
    ):
        raise RoutingInputError(
            f"Checkpoint {index} must be (latitude, longitude)."
        )

    lat, lon = checkpoint

    if (
        isinstance(lat, bool)
        or isinstance(lon, bool)
        or not isinstance(lat, Real)
        or not isinstance(lon, Real)
    ):
        raise RoutingInputError(
            f"Checkpoint {index} coordinates must be numeric."
        )

    lat, lon = float(lat), float(lon)

    if (
        not math.isfinite(lat)
        or not math.isfinite(lon)
        or not -90 <= lat <= 90
        or not -180 <= lon <= 180
    ):
        raise RoutingInputError(
            f"Checkpoint {index} coordinates are invalid."
        )

    return lat, lon


def _point_to_segment_projection(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
) -> tuple[float, float]:
    """
    Return (fraction, offset_miles) for the closest point on a segment.

    Coordinates are (latitude, longitude) for point and
    (longitude, latitude) for route vertices.

    The local equirectangular projection is an approximation intended
    for nearby route geometry, not long-distance geodesic calculations.
    """
    lat_p, lon_p = point
    lon_a, lat_a = start
    lon_b, lat_b = end

    ref_lat = math.radians((lat_a + lat_b + lat_p) / 3.0)
    miles_per_degree_lat = 69.0
    miles_per_degree_lon = 69.0 * math.cos(ref_lat)

    # Normalize longitude differences to the shortest angular direction.
    delta_lon_b = (lon_b - lon_a + 180.0) % 360.0 - 180.0
    delta_lon_p = (lon_p - lon_a + 180.0) % 360.0 - 180.0

    bx = delta_lon_b * miles_per_degree_lon
    by = (lat_b - lat_a) * miles_per_degree_lat
    px = delta_lon_p * miles_per_degree_lon
    py = (lat_p - lat_a) * miles_per_degree_lat

    segment_squared = bx * bx + by * by

    if segment_squared == 0.0:
        return 0.0, math.hypot(px, py)

    fraction = (px * bx + py * by) / segment_squared
    fraction = max(0.0, min(1.0, fraction))

    closest_x = fraction * bx
    closest_y = fraction * by

    offset = math.hypot(px - closest_x, py - closest_y)
    return fraction, offset


class RouteProjector:
    """Precompute route distances and project checkpoints onto the route."""

    __slots__ = (
        "_vertices",
        "_cumulative",
        "_total_miles",
        "_duration_seconds",
    )

    def __init__(self, route: RouteDict) -> None:
        if not isinstance(route, dict):
            raise RoutingInputError("route must be a dictionary.")

        duration_seconds = _validate_number(
            route.get("duration_seconds"),
            "route duration_seconds",
        )
        distance_meters = _validate_number(
            route.get("distance_meters"),
            "route distance_meters",
        )

        if duration_seconds <= 0:
            raise RoutingInputError(
                "route duration_seconds must be greater than zero."
            )

        if distance_meters <= 0:
            raise RoutingInputError(
                "route distance_meters must be greater than zero."
            )

        vertices = _validate_geometry(route.get("geometry"))

        cumulative = [0.0]

        for (lon_a, lat_a), (lon_b, lat_b) in zip(
            vertices, vertices[1:]
        ):
            segment_miles = haversine_distance(
                lat_a, lon_a, lat_b, lon_b
            )

            if not math.isfinite(segment_miles) or segment_miles < 0:
                raise RoutingInputError(
                    "Route geometry has an invalid segment."
                )

            cumulative.append(cumulative[-1] + segment_miles)

        total_miles = cumulative[-1]

        if total_miles <= 0:
            raise RoutingInputError(
                "Route geometry must have a positive total distance."
            )

        declared_miles = distance_meters / METERS_PER_MILE

        # A large mismatch often indicates incorrect coordinates, units,
        # or a geometry/distance pair from different routes.
        # This is deliberately a broad sanity check.
        if not math.isclose(
            declared_miles,
            total_miles,
            rel_tol=DISTANCE_MISMATCH_REL_TOL,
            abs_tol=DISTANCE_MISMATCH_ABS_TOL_MILES,
        ):
            raise RoutingInputError(
                f"Route distance_meters implies {declared_miles:.2f} mi, "
                f"but geometry totals {total_miles:.2f} mi."
            )

        self._vertices = vertices
        self._cumulative = cumulative
        self._total_miles = total_miles
        self._duration_seconds = duration_seconds

    @property
    def total_miles(self) -> float:
        return self._total_miles

    @property
    def duration_seconds(self) -> float:
        return self._duration_seconds

    def __len__(self) -> int:
        return len(self._vertices)

    def project(self, point: tuple[float, float]) -> _Projection:
        """Project (latitude, longitude) onto the nearest route segment."""
        best_offset = math.inf
        best_distance_along = 0.0

        for index, (start, end) in enumerate(
            zip(self._vertices, self._vertices[1:])
        ):
            fraction, offset = _point_to_segment_projection(
                point, start, end
            )

            if offset >= best_offset:
                continue

            segment_start = self._cumulative[index]
            segment_end = self._cumulative[index + 1]
            segment_length = segment_end - segment_start

            best_distance_along = (
                segment_start + fraction * segment_length
            )
            best_offset = offset

        return _Projection(
            distance_miles=best_distance_along,
            offset_miles=best_offset,
        )

    def eta_for(
        self,
        checkpoint_distance_miles: float,
        departure_utc: datetime,
    ) -> datetime:
        """Calculate ETA for a cumulative distance along the route."""
        distance = _validate_number(
            checkpoint_distance_miles,
            "checkpoint_distance_miles",
        )

        if distance > self._total_miles + ORDER_TOLERANCE_MILES:
            raise RoutingInputError(
                "Checkpoint distance cannot exceed route length."
            )

        distance = min(distance, self._total_miles)
        fraction = distance / self._total_miles

        return departure_utc + timedelta(
            seconds=self._duration_seconds * fraction
        )


def estimate_checkpoint_etas(
    route: RouteDict,
    departure_time: datetime,
    checkpoints: Sequence[tuple[float, float]],
    *,
    max_checkpoint_offset_miles: float = (
        DEFAULT_MAX_CHECKPOINT_OFFSET_MILES
    ),
) -> list[CheckpointETA]:
    """
    Estimate ETAs for ordered checkpoints along a route.

    Checkpoints must be (latitude, longitude) pairs and should be supplied
    in travel order. Returned timestamps are timezone-aware UTC datetimes.

    ETA is estimated proportionally from cumulative distance and total
    route duration. This assumes constant average speed and is not a
    segment-specific traffic prediction.
    """
    max_offset = _validate_number(
        max_checkpoint_offset_miles,
        "max_checkpoint_offset_miles",
    )

    departure_utc = _normalize_departure_time(departure_time)
    projector = RouteProjector(route)

    if not isinstance(checkpoints, (list, tuple)) or not checkpoints:
        raise RoutingInputError(
            "checkpoints must be a non-empty sequence."
        )

    results: list[CheckpointETA] = []
    previous_distance = -math.inf

    for index, raw_checkpoint in enumerate(checkpoints):
        checkpoint = _validate_checkpoint(raw_checkpoint, index)
        projection = projector.project(checkpoint)

        if projection.offset_miles > max_offset:
            raise RoutingInputError(
                f"Checkpoint {index} is {projection.offset_miles:.2f} mi "
                f"from the route; maximum allowed is {max_offset:.2f} mi."
            )

        if (
            projection.distance_miles + ORDER_TOLERANCE_MILES
            < previous_distance
        ):
            raise RoutingInputError(
                f"Checkpoint {index} is out of route order."
            )

        previous_distance = projection.distance_miles

        results.append(
            CheckpointETA(
                distance_miles=projection.distance_miles,
                arrival_time=projector.eta_for(
                    projection.distance_miles,
                    departure_utc,
                ),
            )
        )

    return results
