
import math


EARTH_RADIUS_MILES = 3958.8


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate the great-circle distance between two GPS coordinates.

    Args:
        lat1: Starting latitude in degrees.
        lon1: Starting longitude in degrees.
        lat2: Ending latitude in degrees.
        lon2: Ending longitude in degrees.

    Returns:
        Approximate surface distance in miles.
    """
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )

    # Guard against floating-point rounding errors.
    a = max(0.0, min(1.0, a))

    central_angle = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1.0 - a),
    )

    return EARTH_RADIUS_MILES * central_angle
