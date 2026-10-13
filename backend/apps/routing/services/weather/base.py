
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from numbers import Real
from typing import Final


# --------------------------------------------------------------- units

WIND_UNIT: Final = "mph"
PRECIPITATION_UNIT: Final = "inches"
SNOWFALL_UNIT: Final = "inches"


# --------------------------------------------------------- request bounds

MIN_FORECAST_HOURS: Final = 1
MAX_FORECAST_HOURS: Final = 24 * 14

_LAT_MIN: Final = -90.0
_LAT_MAX: Final = 90.0
_LON_MIN: Final = -180.0
_LON_MAX: Final = 180.0


__all__ = [
    "WIND_UNIT",
    "PRECIPITATION_UNIT",
    "SNOWFALL_UNIT",
    "MIN_FORECAST_HOURS",
    "MAX_FORECAST_HOURS",
    "HourlyWeather",
    "WeatherError",
    "WeatherInputError",
    "WeatherProviderError",
    "WeatherProvider",
]


# ------------------------------------------------------------- helpers


def _is_finite_number(value: object) -> bool:
    """Return True for finite real numbers, excluding booleans."""
    if isinstance(value, bool) or not isinstance(value, Real):
        return False

    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def _require_aware_datetime(
    value: object,
    label: str,
) -> datetime:
    """Return a timezone-aware datetime or raise ValueError."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(
            f"{label} must be a timezone-aware datetime."
        )

    return value


def _coerce_optional_non_negative(
    value: object,
    label: str,
) -> float | None:
    """Normalize a non-negative finite number to float; preserve None."""
    if value is None:
        return None

    if not _is_finite_number(value) or value < 0:
        raise ValueError(
            f"{label} must be a finite, non-negative number or None."
        )

    return float(value)


def _utc_timestamp(value: datetime) -> float:
    """Convert an aware datetime to a comparable UTC timestamp."""
    return value.timestamp()


# ------------------------------------------------------------ data model


@dataclass(frozen=True, slots=True)
class HourlyWeather:
    """
    Normalized weather data for one forecast timestamp.

    Units:
        wind_mph: miles per hour
        precipitation_inches: inches accumulated over the provider's
            documented precipitation interval
        snowfall_inches: inches accumulated over the provider's
            documented snowfall interval

    None means the measurement is unavailable, not zero.
    """

    timestamp: datetime
    wind_mph: float | None
    precipitation_inches: float | None
    snowfall_inches: float | None

    def __post_init__(self) -> None:
        _require_aware_datetime(self.timestamp, "timestamp")

        for name in (
            "wind_mph",
            "precipitation_inches",
            "snowfall_inches",
        ):
            value = _coerce_optional_non_negative(
                getattr(self, name),
                name,
            )
            object.__setattr__(self, name, value)


# ------------------------------------------------------------ exceptions


class WeatherError(Exception):
    """Base class for weather-related errors."""


class WeatherInputError(WeatherError, ValueError):
    """Raised when weather request inputs are invalid."""


class WeatherProviderError(WeatherError):
    """Raised when a provider cannot return usable weather data."""


# -------------------------------------------------------------- contract


class WeatherProvider(ABC):
    """
    Contract implemented by each weather provider.

    Concrete providers must normalize returned values to the units
    defined above and return records in chronological order.

    Missing forecast values must remain None.
    """

    name: str = "WeatherProvider"
    is_async: bool = False

    @abstractmethod
    def get_hourly_forecast(
        self,
        latitude: float,
        longitude: float,
        start: datetime,
        end: datetime,
    ) -> list[HourlyWeather]:
        """
        Return available hourly weather records for [start, end].

        Both boundaries are inclusive. Results must be ordered by
        timestamp and contain no duplicate timestamps. Missing hours
        may be absent; callers must not assume every hour is present.

        Raises:
            WeatherInputError: Invalid coordinates or time window.
            WeatherProviderError: Provider failure or invalid response.
        """
        raise NotImplementedError

    # ---------------------------------------------------- validation

    def _validate_request(
        self,
        latitude: float,
        longitude: float,
        start: datetime,
        end: datetime,
    ) -> None:
        """Validate coordinates and the requested forecast window."""
        self._validate_coordinates(latitude, longitude)
        self._validate_window(start, end)

    def _validate_coordinates(
        self,
        latitude: float,
        longitude: float,
    ) -> None:
        if (
            not _is_finite_number(latitude)
            or not _LAT_MIN <= latitude <= _LAT_MAX
        ):
            raise WeatherInputError(
                f"latitude must be between {_LAT_MIN} and {_LAT_MAX}."
            )

        if (
            not _is_finite_number(longitude)
            or not _LON_MIN <= longitude <= _LON_MAX
        ):
            raise WeatherInputError(
                f"longitude must be between {_LON_MIN} and {_LON_MAX}."
            )

    def _validate_window(
        self,
        start: datetime,
        end: datetime,
    ) -> None:
        try:
            start = _require_aware_datetime(start, "start")
            end = _require_aware_datetime(end, "end")
        except ValueError as exc:
            raise WeatherInputError(str(exc)) from exc

        # Compare actual instants, including datetimes with different
        # timezone offsets.
        duration_seconds = (
            _utc_timestamp(end) - _utc_timestamp(start)
        )
        window_hours = duration_seconds / 3600.0

        if window_hours < 0:
            raise WeatherInputError(
                "end must be on or after start."
            )

        if window_hours < MIN_FORECAST_HOURS:
            raise WeatherInputError(
                f"forecast window must be at least "
                f"{MIN_FORECAST_HOURS} hour(s)."
            )

        if window_hours > MAX_FORECAST_HOURS:
            raise WeatherInputError(
                f"forecast window must not exceed "
                f"{MAX_FORECAST_HOURS} hours."
            )

    # ---------------------------------------------------------- repr

    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.name!r}>"
