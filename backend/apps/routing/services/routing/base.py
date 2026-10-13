
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections.abc import Mapping
from numbers import Real
from typing import Any, Final, TypeAlias, TypedDict





Coordinate: TypeAlias = tuple[float, float]

GeometryVertex: TypeAlias = list[float]


class RouteDict(TypedDict):
    """Standard route representation returned by every provider."""

    geometry: list[GeometryVertex]
    distance_meters: float
    duration_seconds: float





class RoutingError(Exception):
    """Base exception for routing-related failures."""


class RoutingInputError(RoutingError, ValueError):
    """Raised when routing inputs or options are invalid."""


class RoutingProviderError(RoutingError):
    """Raised when an upstream routing provider fails."""




DEFAULT_ALTERNATIVES: Final[int] = 3
MAX_ALTERNATIVES: Final[int] = 10

LATITUDE_RANGE: Final[tuple[float, float]] = (-90.0, 90.0)
LONGITUDE_RANGE: Final[tuple[float, float]] = (-180.0, 180.0)

__all__ = [
    "Coordinate",
    "GeometryVertex",
    "RouteDict",
    "RoutingError",
    "RoutingInputError",
    "RoutingProviderError",
    "RoutingProvider",
    "DEFAULT_ALTERNATIVES",
    "MAX_ALTERNATIVES",
]




def _validate_coordinate(value: Any, label: str) -> None:
    """Validate a (latitude, longitude) coordinate pair."""

    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise RoutingInputError(
            f"{label!r} must be a (latitude, longitude) pair."
        )

    lat, lon = value

    # Reject booleans explicitly: bool is a subclass of int.
    if (
        isinstance(lat, bool)
        or isinstance(lon, bool)
        or not isinstance(lat, Real)
        or not isinstance(lon, Real)
    ):
        raise RoutingInputError(
            f"{label!r} coordinates must be numeric."
        )

    try:
        lat_float = float(lat)
        lon_float = float(lon)
    except (OverflowError, ValueError) as exc:
        raise RoutingInputError(
            f"{label!r} coordinates must be finite numbers."
        ) from exc

    if not math.isfinite(lat_float) or not math.isfinite(lon_float):
        raise RoutingInputError(
            f"{label!r} coordinates must be finite numbers."
        )

    if not LATITUDE_RANGE[0] <= lat_float <= LATITUDE_RANGE[1]:
        raise RoutingInputError(
            f"{label!r} latitude must be between "
            f"{LATITUDE_RANGE[0]} and {LATITUDE_RANGE[1]}."
        )

    if not LONGITUDE_RANGE[0] <= lon_float <= LONGITUDE_RANGE[1]:
        raise RoutingInputError(
            f"{label!r} longitude must be between "
            f"{LONGITUDE_RANGE[0]} and {LONGITUDE_RANGE[1]}."
        )





class RoutingProvider(ABC):
    """
    Common contract for routing-provider adapters.

    Inputs use (latitude, longitude).
    Output geometry uses [longitude, latitude].

    Every concrete provider must implement get_routes() and
    call _validate_request() before making its upstream request.
    """

    name: str = "RoutingProvider"

    def _validate_request(
        self,
        origin: Coordinate,
        destination: Coordinate,
        alternatives: int = DEFAULT_ALTERNATIVES,
    ) -> None:
        """Validate shared routing arguments."""

        _validate_coordinate(origin, "origin")
        _validate_coordinate(destination, "destination")

        if (
            isinstance(alternatives, bool)
            or not isinstance(alternatives, int)
        ):
            raise RoutingInputError(
                "'alternatives' must be an integer."
            )

        if not 1 <= alternatives <= MAX_ALTERNATIVES:
            raise RoutingInputError(
                f"'alternatives' must be between 1 and "
                f"{MAX_ALTERNATIVES}; received {alternatives}."
            )

    @abstractmethod
    def get_routes(
        self,
        origin: Coordinate,
        destination: Coordinate,
        *,
        alternatives: int = DEFAULT_ALTERNATIVES,
    ) -> list[RouteDict]:
        """
        Retrieve candidate routes, ordered best first.

        Return an empty list if no route is available.

        Raise:
            RoutingInputError: Invalid coordinates or options.
            RoutingProviderError: Upstream request or response failure.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.name!r}>"
