
"""Address-to-coordinate geocoding adapter."""

from __future__ import annotations

import math
import threading
import time
from collections import OrderedDict
from typing import Any, Final, Protocol

from geopy.exc import (
    GeocoderQueryError,
    GeocoderRateLimited,
    GeocoderServiceError,
    GeocoderTimedOut,
)
from geopy.geocoders import Nominatim

from apps.routing.services.routing.base import (
    Coordinate,
    RoutingInputError,
    RoutingProviderError,
)

DEFAULT_TIMEOUT_SECONDS: Final[float] = 5.0
MIN_ADDRESS_LENGTH: Final[int] = 2
MAX_ADDRESS_LENGTH: Final[int] = 500
MIN_USER_AGENT_LENGTH: Final[int] = 8
NOMINATIM_MIN_INTERVAL_SECONDS: Final[float] = 1.0
DEFAULT_CACHE_SIZE: Final[int] = 256


class _GeocoderClient(Protocol):
    """Interface implemented by geopy clients and test doubles."""

    def geocode(
        self,
        query: str,
        *,
        exactly_one: bool = True,
        addressdetails: bool = False,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Any: ...


class Geocoder:
    """Resolve addresses to validated (latitude, longitude) coordinates.

    Includes address validation, a bounded LRU cache and a per-instance
    request rate limiter.

    The public Nominatim endpoint is intended for low-volume use. The
    rate limiter is per instance, not global across processes.
    """

    __slots__ = (
        "_client",
        "_timeout",
        "_owns_client",
        "_min_interval",
        "_lock",
        "_last_call_at",
        "_cache",
        "_cache_size",
    )

    def __init__(
        self,
        *,
        user_agent: str,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        client: _GeocoderClient | None = None,
        min_interval_seconds: float = NOMINATIM_MIN_INTERVAL_SECONDS,
        cache_size: int = DEFAULT_CACHE_SIZE,
    ) -> None:
        self._validate_user_agent(user_agent)
        self._validate_positive_finite(timeout, "timeout")
        self._validate_non_negative_finite(
            min_interval_seconds, "min_interval_seconds"
        )
        self._validate_cache_size(cache_size)

        self._timeout = float(timeout)
        self._min_interval = float(min_interval_seconds)
        self._cache_size = cache_size
        self._cache: OrderedDict[str, Coordinate] = OrderedDict()

        self._owns_client = client is None
        self._client: _GeocoderClient = (
            client
            if client is not None
            else Nominatim(
                user_agent=user_agent.strip(),
                timeout=self._timeout,
            )
        )

        # Protects cache and request timing state.
        self._lock = threading.Lock()
        self._last_call_at = 0.0

    def close(self) -> None:
        """Close the client only when this instance created it."""
        close = getattr(self._client, "close", None)
        if self._owns_client and callable(close):
            close()

    def __enter__(self) -> Geocoder:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def geocode(
        self,
        address: str,
        *,
        language: str | None = None,
        country_codes: str | None = None,
    ) -> Coordinate:
        """Resolve an address to decimal-degree coordinates.

        Args:
            address: Human-readable address.
            language: Optional preferred language, such as ``"en"``.
            country_codes: Optional comma-separated ISO alpha-2 codes,
                such as ``"in,us"``.

        Raises:
            RoutingInputError: Invalid input.
            RoutingProviderError: Provider failure or no matching result.
        """
        normalized = self._validate_address(address)
        language = self._validate_optional_string(language, "language")
        country_codes = self._validate_country_codes(country_codes)

        cache_key = self._cache_key(normalized, language, country_codes)

        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        extra: dict[str, str] = {}
        if language is not None:
            extra["language"] = language
        if country_codes is not None:
            extra["country_codes"] = country_codes

        self._respect_rate_limit()

        try:
            result = self._client.geocode(
                normalized,
                exactly_one=True,
                addressdetails=False,
                timeout=self._timeout,
                **extra,
            )
        except GeocoderTimedOut as exc:
            raise RoutingProviderError(
                f"Geocoding timed out for {normalized!r}."
            ) from exc
        except GeocoderRateLimited as exc:
            raise RoutingProviderError(
                f"Geocoding rate-limited for {normalized!r}; retry later."
            ) from exc
        except GeocoderQueryError as exc:
            raise RoutingProviderError(
                f"Geocoding provider rejected {normalized!r}."
            ) from exc
        except GeocoderServiceError as exc:
            raise RoutingProviderError(
                f"Geocoding service error for {normalized!r}."
            ) from exc

        if result is None:
            raise RoutingProviderError(
                f"No coordinates found for address: {normalized!r}"
            )

        coordinate = self._extract_coordinate(result, normalized)
        self._cache_put(cache_key, coordinate)
        return coordinate

    def _respect_rate_limit(self) -> None:
        """Serialize calls and enforce the configured interval."""
        with self._lock:
            now = time.monotonic()
            wait = self._min_interval - (now - self._last_call_at)
            if wait > 0:
                time.sleep(wait)
            self._last_call_at = time.monotonic()

    @staticmethod
    def _cache_key(
        address: str,
        language: str | None,
        country_codes: str | None,
    ) -> str:
        return f"{address}|{language or ''}|{country_codes or ''}"

    def _cache_get(self, key: str) -> Coordinate | None:
        with self._lock:
            value = self._cache.get(key)
            if value is not None:
                self._cache.move_to_end(key)
            return value

    def _cache_put(self, key: str, value: Coordinate) -> None:
        if self._cache_size == 0:
            return

        with self._lock:
            self._cache[key] = value
            self._cache.move_to_end(key)

            while len(self._cache) > self._cache_size:
                self._cache.popitem(last=False)

    @staticmethod
    def _extract_coordinate(result: Any, address: str) -> Coordinate:
        try:
            latitude = float(result.latitude)
            longitude = float(result.longitude)
        except (AttributeError, TypeError, ValueError, OverflowError) as exc:
            raise RoutingProviderError(
                f"Geocoder returned invalid coordinates for {address!r}."
            ) from exc

        if (
            not math.isfinite(latitude)
            or not math.isfinite(longitude)
            or not -90.0 <= latitude <= 90.0
            or not -180.0 <= longitude <= 180.0
        ):
            raise RoutingProviderError(
                f"Geocoder returned out-of-bounds coordinates for {address!r}."
            )

        return latitude, longitude

    @staticmethod
    def _validate_user_agent(user_agent: str) -> None:
        if not isinstance(user_agent, str):
            raise RoutingInputError("user_agent must be a string.")

        value = user_agent.strip()
        if len(value) < MIN_USER_AGENT_LENGTH:
            raise RoutingInputError(
                f"user_agent must contain at least "
                f"{MIN_USER_AGENT_LENGTH} characters."
            )

        if "@" not in value and "://" not in value:
            raise RoutingInputError(
                "user_agent must identify your application and provide "
                "a contact email or URL."
            )

    @staticmethod
    def _validate_positive_finite(value: float, name: str) -> None:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value <= 0
        ):
            raise RoutingInputError(f"{name} must be a positive finite number.")

    @staticmethod
    def _validate_non_negative_finite(value: float, name: str) -> None:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise RoutingInputError(
                f"{name} must be a non-negative finite number."
            )

    @staticmethod
    def _validate_cache_size(size: int) -> None:
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise RoutingInputError(
                "cache_size must be a non-negative integer."
            )

    @staticmethod
    def _validate_address(address: str) -> str:
        if not isinstance(address, str):
            raise RoutingInputError("Address must be a string.")

        normalized = " ".join(address.split())

        if not MIN_ADDRESS_LENGTH <= len(normalized) <= MAX_ADDRESS_LENGTH:
            raise RoutingInputError(
                f"Address must contain {MIN_ADDRESS_LENGTH} to "
                f"{MAX_ADDRESS_LENGTH} characters."
            )

        return normalized

    @staticmethod
    def _validate_optional_string(
        value: str | None,
        name: str,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str) or not value.strip():
            raise RoutingInputError(
                f"{name} must be a non-empty string when provided."
            )

        return value.strip()

    @staticmethod
    def _validate_country_codes(value: str | None) -> str | None:
        value = Geocoder._validate_optional_string(value, "country_codes")
        if value is None:
            return None

        codes = [part.strip().lower() for part in value.split(",")]
        if not codes or any(
            len(code) != 2 or not code.isalpha() or not code.isascii()
            for code in codes
        ):
            raise RoutingInputError(
                "country_codes must be comma-separated two-letter "
                "ISO country codes, such as 'in,us'."
            )

        return ",".join(dict.fromkeys(codes))


__all__ = ["Geocoder"]
