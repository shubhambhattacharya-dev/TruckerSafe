
from __future__ import annotations

import math
from numbers import Real
from typing import Any, Final

import requests

from .base import (
    Coordinate,
    RouteDict,
    RoutingInputError,
    RoutingProvider,
    RoutingProviderError,
    DEFAULT_ALTERNATIVES,
)


OSRM_BASE_URL: Final = "https://router.project-osrm.org"
REQUEST_TIMEOUT_SECONDS: Final = 15.0
USER_AGENT: Final = "truckersafe/1.0"

_LON_MIN: Final = -180.0
_LON_MAX: Final = 180.0
_LAT_MIN: Final = -90.0
_LAT_MAX: Final = 90.0


def _is_finite_number(value: Any) -> bool:
    """Accept finite real numbers, but reject booleans."""
    if isinstance(value, bool) or not isinstance(value, Real):
        return False

    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


class OSRMAdapter(RoutingProvider):
    """Retrieve and normalize road routes from OSRM."""

    name = "OSRM"
    is_async = False

    def __init__(
        self,
        base_url: str = OSRM_BASE_URL,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("base_url must be a non-empty string.")

        if (
            not _is_finite_number(timeout)
            or timeout <= 0
        ):
            raise ValueError("timeout must be a positive finite number.")

        self.base_url = base_url.strip().rstrip("/")
        self.timeout = float(timeout)

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": USER_AGENT})
        self._closed = False

    # ------------------------------------------------ lifecycle

    def close(self) -> None:
        """Release the underlying HTTP connection pool."""
        if not self._closed:
            self._session.close()
            self._closed = True

    def __enter__(self) -> OSRMAdapter:
        if self._closed:
            raise RuntimeError("OSRMAdapter is already closed.")
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # ------------------------------------------------ public API

    def get_routes(
        self,
        origin: Coordinate,
        destination: Coordinate,
        *,
        alternatives: int = DEFAULT_ALTERNATIVES,
    ) -> list[RouteDict]:
        self._ensure_open()
        self._validate_request(origin, destination, alternatives)

        if origin == destination:
            raise RoutingInputError(
                "Origin and destination must be different."
            )

        # Application contract: (latitude, longitude).
        # OSRM URL: longitude,latitude.
        coordinates = (
            f"{origin[1]},{origin[0]};"
            f"{destination[1]},{destination[0]}"
        )

        url = f"{self.base_url}/route/v1/driving/{coordinates}"
        # OSRM's `alternatives` query parameter counts EXTRA routes beyond
        # the primary route, while this adapter's contract counts TOTAL
        # routes. Request one fewer extra route so the provider can never
        # exceed the requested total (main + N-1 extras <= N).
        osrm_alternatives = max(0, alternatives - 1)
        payload = self._fetch(url, osrm_alternatives)
        raw_routes = self._extract_routes(payload)

        routes = [self._parse_route(route) for route in raw_routes]

        if len(routes) > alternatives:
            raise RoutingProviderError(
                "OSRM returned more routes than requested."
            )

        # OSRM can return fewer alternatives than requested.
        # Never fabricate routes to meet the requested count.
        return routes

    # ------------------------------------------------ internals

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("OSRMAdapter is closed.")

    def _fetch(
        self,
        url: str,
        alternatives: int,
    ) -> dict[str, Any]:
        params = {
            "alternatives": alternatives,
            "overview": "full",
            "geometries": "geojson",
            "steps": "false",
        }

        try:
            response = self._session.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()

        except requests.Timeout as exc:
            raise RoutingProviderError(
                f"OSRM request timed out after {self.timeout}s."
            ) from exc

        except requests.RequestException as exc:
            raise RoutingProviderError(
                f"OSRM request failed: {exc}"
            ) from exc

        try:
            payload = response.json()
        except (ValueError, requests.exceptions.JSONDecodeError) as exc:
            raise RoutingProviderError(
                "OSRM returned invalid JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise RoutingProviderError(
                "OSRM returned an unexpected response shape."
            )

        if payload.get("code") != "Ok":
            message = payload.get("message", "Unknown OSRM error")
            raise RoutingProviderError(
                f"OSRM routing failed: {message}"
            )

        return payload

    def _extract_routes(
        self,
        payload: dict[str, Any],
    ) -> list[Any]:
        routes = payload.get("routes")

        if not isinstance(routes, list) or not routes:
            raise RoutingProviderError("OSRM returned no routes.")

        return routes

    def _parse_route(self, raw_route: Any) -> RouteDict:
        if not isinstance(raw_route, dict):
            raise RoutingProviderError(
                "OSRM returned an invalid route entry."
            )

        return {
            "geometry": self._parse_geometry(
                raw_route.get("geometry")
            ),
            "distance_meters": self._parse_non_negative(
                raw_route.get("distance"), "distance"
            ),
            "duration_seconds": self._parse_non_negative(
                raw_route.get("duration"), "duration"
            ),
        }

    def _parse_geometry(self, geometry: Any) -> list[list[float]]:
        if not isinstance(geometry, dict):
            raise RoutingProviderError(
                "OSRM route is missing geometry."
            )

        if geometry.get("type") != "LineString":
            raise RoutingProviderError(
                "OSRM returned an unsupported geometry type."
            )

        coordinates = geometry.get("coordinates")

        if not isinstance(coordinates, list) or len(coordinates) < 2:
            raise RoutingProviderError(
                "OSRM geometry must contain at least two points."
            )

        return [self._parse_vertex(point) for point in coordinates]

    def _parse_vertex(self, point: Any) -> list[float]:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            raise RoutingProviderError(
                "OSRM returned an invalid geometry point."
            )

        lon, lat = point[0], point[1]

        if not _is_finite_number(lon) or not _is_finite_number(lat):
            raise RoutingProviderError(
                "OSRM returned non-numeric coordinates."
            )

        lon = float(lon)
        lat = float(lat)

        if not (
            _LON_MIN <= lon <= _LON_MAX
            and _LAT_MIN <= lat <= _LAT_MAX
        ):
            raise RoutingProviderError(
                "OSRM returned out-of-range coordinates."
            )

        # Preserve GeoJSON order: [longitude, latitude].
        return [lon, lat]

    def _parse_non_negative(
        self,
        value: Any,
        label: str,
    ) -> float:
        if not _is_finite_number(value) or value < 0:
            raise RoutingProviderError(
                f"OSRM returned invalid {label}."
            )

        # Important: return the numeric value, not a boolean.
        return float(value)
