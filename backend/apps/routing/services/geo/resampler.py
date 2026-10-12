
import math
from typing import List, Tuple

from .haversine import haversine_distance


Coordinate = Tuple[float, float]

DESTINATION_TOLERANCE_MILES = 1e-6
ANTIPODAL_TOLERANCE = 1e-12


def resample_polyline(
    points: List[Coordinate],
    interval_miles: float = 25.0,
) -> List[Coordinate]:
    """
    Generate checkpoints at regular cumulative-distance intervals.

    Coordinates are (latitude, longitude) pairs in degrees.
    Distances are measured in miles using haversine_distance().

    The start and destination are preserved. Intermediate checkpoints
    are interpolated along the great-circle arc between route vertices.

    Raises:
        ValueError: If the interval or coordinates are invalid, or if a
                    segment is nearly antipodal and interpolation is
                    ambiguous.
    """
    if (
        isinstance(interval_miles, bool)
        or not isinstance(interval_miles, (int, float))
        or not math.isfinite(interval_miles)
        or interval_miles <= 0
    ):
        raise ValueError(
            "interval_miles must be a finite positive number"
        )

    if not points:
        return []

    _validate_coordinates(points)

    if len(points) == 1:
        return [tuple(points[0])]

    checkpoints: List[Coordinate] = [tuple(points[0])]
    cumulative_distance = 0.0
    next_checkpoint_distance = float(interval_miles)

    for i in range(1, len(points)):
        start = tuple(points[i - 1])
        end = tuple(points[i])

        segment_distance = haversine_distance(
            start[0],
            start[1],
            end[0],
            end[1],
        )

        if not math.isfinite(segment_distance) or segment_distance < 0:
            raise ValueError(
                f"Invalid segment distance at index {i - 1}"
            )

        # Skip duplicate consecutive coordinates.
        if segment_distance == 0:
            continue

        segment_end_distance = cumulative_distance + segment_distance

        # Create every checkpoint target contained in this segment.
        while next_checkpoint_distance <= segment_end_distance:
            distance_into_segment = (
                next_checkpoint_distance - cumulative_distance
            )

            fraction = distance_into_segment / segment_distance
            fraction = max(0.0, min(1.0, fraction))

            checkpoint = _interpolate_coordinates(
                start,
                end,
                fraction,
            )

            checkpoints.append(checkpoint)
            next_checkpoint_distance += float(interval_miles)

        cumulative_distance = segment_end_distance

    destination = tuple(points[-1])
    last_checkpoint = checkpoints[-1]

    destination_gap = haversine_distance(
        last_checkpoint[0],
        last_checkpoint[1],
        destination[0],
        destination[1],
    )

    if destination_gap > DESTINATION_TOLERANCE_MILES:
        checkpoints.append(destination)
    else:
        # Preserve the exact input destination coordinates.
        checkpoints[-1] = destination

    return checkpoints


def _interpolate_coordinates(
    start: Coordinate,
    end: Coordinate,
    fraction: float,
) -> Coordinate:
    """
    Interpolate along the great-circle arc between two coordinates.

    fraction=0 returns start; fraction=1 returns end.
    """
    if not math.isfinite(fraction) or not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be between 0 and 1")

    if fraction == 0.0:
        return start

    if fraction == 1.0:
        return end

    lat1, lon1 = map(math.radians, start)
    lat2, lon2 = map(math.radians, end)

    # Convert both coordinates to 3D unit-sphere vectors.
    x1 = math.cos(lat1) * math.cos(lon1)
    y1 = math.cos(lat1) * math.sin(lon1)
    z1 = math.sin(lat1)

    x2 = math.cos(lat2) * math.cos(lon2)
    y2 = math.cos(lat2) * math.sin(lon2)
    z2 = math.sin(lat2)

    dot = x1 * x2 + y1 * y2 + z1 * z2
    dot = max(-1.0, min(1.0, dot))

    omega = math.acos(dot)

    if omega < ANTIPODAL_TOLERANCE:
        # The endpoints are effectively the same point.
        return start

    sin_omega = math.sin(omega)

    if abs(sin_omega) < ANTIPODAL_TOLERANCE:
        # Nearly antipodal points have an ambiguous great-circle path.
        raise ValueError(
            "Cannot interpolate a nearly antipodal segment reliably"
        )

    weight_start = math.sin((1.0 - fraction) * omega) / sin_omega
    weight_end = math.sin(fraction * omega) / sin_omega

    x = weight_start * x1 + weight_end * x2
    y = weight_start * y1 + weight_end * y2
    z = weight_start * z1 + weight_end * z2

    # Normalize the interpolated vector.
    norm = math.sqrt(x * x + y * y + z * z)

    if norm == 0.0:
        raise ValueError("Interpolation produced an invalid coordinate")

    x /= norm
    y /= norm
    z /= norm

    latitude = math.degrees(math.asin(max(-1.0, min(1.0, z))))
    longitude = math.degrees(math.atan2(y, x))

    return latitude, longitude


def _validate_coordinates(points: List[Coordinate]) -> None:
    """Validate coordinate structure, types, and geographic ranges."""
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
                f"Point at index {index} must have numeric coordinates"
            )

        if not math.isfinite(latitude) or not math.isfinite(longitude):
            raise ValueError(
                f"Point at index {index} must contain finite coordinates"
            )

        if not -90 <= latitude <= 90:
            raise ValueError(
                f"Latitude at index {index} must be between -90 and 90"
            )

        if not -180 <= longitude <= 180:
            raise ValueError(
                f"Longitude at index {index} must be between -180 and 180"
            )
