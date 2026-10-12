
import math
from typing import List, Sequence, Tuple

Coordinate = Tuple[float, float]

_EARTH_RADIUS_MILES = 3958.7613
_DEGREES_TO_RADIANS = math.pi / 180.0


def simplify_polyline(
    points: Sequence[Coordinate],
    tolerance_miles: float = 0.1,
) -> List[Coordinate]:
    """
    Simplify a GPS polyline using the iterative Douglas-Peucker algorithm.

    Args:
        points: Ordered GPS coordinates as (latitude, longitude).
        tolerance_miles: Maximum permitted deviation, approximately, in miles.

    Returns:
        A simplified list of GPS coordinates.

    Note:
        Distance calculations use a local equirectangular projection.
        The tolerance is approximate, not a strict global error bound.
    """
    _validate_tolerance(tolerance_miles)

    points = list(points)
    _validate_coordinates(points)

    result = [(float(lat), float(lon)) for lat, lon in points]

    if len(result) <= 2 or tolerance_miles == 0:
        return result

    keep_indices = _douglas_peucker_indices(
        result,
        tolerance_miles,
    )

    return [result[index] for index in keep_indices]


def _douglas_peucker_indices(
    points: Sequence[Coordinate],
    tolerance_miles: float,
) -> List[int]:
    """Return retained point indices without recursive function calls."""
    n = len(points)

    keep = [False] * n
    keep[0] = True
    keep[-1] = True

    stack = [(0, n - 1)]

    while stack:
        start_idx, end_idx = stack.pop()

        if end_idx <= start_idx + 1:
            continue

        start = points[start_idx]
        end = points[end_idx]

        max_distance = -1.0
        max_idx = -1

        for index in range(start_idx + 1, end_idx):
            distance = _point_segment_distance_miles(
                points[index],
                start,
                end,
            )

            if distance > max_distance:
                max_distance = distance
                max_idx = index

        if max_idx >= 0 and max_distance > tolerance_miles:
            keep[max_idx] = True
            stack.append((max_idx, end_idx))
            stack.append((start_idx, max_idx))

    return [
        index
        for index, should_keep in enumerate(keep)
        if should_keep
    ]


def _point_segment_distance_miles(
    point: Coordinate,
    start: Coordinate,
    end: Coordinate,
) -> float:
    """
    Approximate point-to-segment distance using a local projection.

    Longitudes are unwrapped relative to the segment start so that
    routes crossing the antimeridian use the shorter longitude difference.
    """
    lat0, lon0 = start
    lat1, lon1 = end
    latp, lonp = point

    reference_lat = (
        (lat0 + lat1 + latp) / 3.0
    ) * _DEGREES_TO_RADIANS

    # Convert the three coordinates into local x/y distances in miles.
    x_scale = _EARTH_RADIUS_MILES * math.cos(reference_lat) * _DEGREES_TO_RADIANS
    y_scale = _EARTH_RADIUS_MILES * _DEGREES_TO_RADIANS

    dx = _longitude_delta(lon1, lon0) * x_scale
    dy = (lat1 - lat0) * y_scale

    px = _longitude_delta(lonp, lon0) * x_scale
    py = (latp - lat0) * y_scale

    segment_length_squared = dx * dx + dy * dy

    if segment_length_squared == 0.0:
        return math.hypot(px, py)

    projection = (px * dx + py * dy) / segment_length_squared
    projection = max(0.0, min(1.0, projection))

    closest_x = projection * dx
    closest_y = projection * dy

    return math.hypot(px - closest_x, py - closest_y)


def _longitude_delta(lon_a: float, lon_b: float) -> float:
    """Return the shortest signed longitude difference in degrees."""
    return (lon_a - lon_b + 180.0) % 360.0 - 180.0


def _validate_tolerance(tolerance_miles: float) -> None:
    if (
        isinstance(tolerance_miles, bool)
        or not isinstance(tolerance_miles, (int, float))
        or not math.isfinite(tolerance_miles)
        or tolerance_miles < 0
    ):
        raise ValueError(
            "tolerance_miles must be a finite non-negative number"
        )


def _validate_coordinates(points: Sequence[Coordinate]) -> None:
    """Validate every latitude/longitude pair."""
    for index, point in enumerate(points):
        if not isinstance(point, (tuple, list)) or len(point) != 2:
            raise ValueError(
                f"Point at index {index} must contain latitude and longitude"
            )

        latitude, longitude = point

        if (
            isinstance(latitude, bool)
            or isinstance(longitude, bool)
            or not isinstance(latitude, (int, float))
            or not isinstance(longitude, (int, float))
        ):
            raise ValueError(
                f"Coordinates at index {index} must be numeric"
            )

        if not math.isfinite(latitude) or not math.isfinite(longitude):
            raise ValueError(
                f"Coordinates at index {index} must be finite"
            )

        if not -90 <= latitude <= 90:
            raise ValueError(
                f"Latitude at index {index} must be between -90 and 90"
            )

        if not -180 <= longitude <= 180:
            raise ValueError(
                f"Longitude at index {index} must be between -180 and 180"
            )
