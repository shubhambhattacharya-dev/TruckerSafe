
from __future__ import annotations

from bisect import bisect_left
from datetime import datetime, timezone
from numbers import Real
from typing import Final, NamedTuple, Sequence

from apps.routing.services.weather.base import (
    HourlyWeather,
    WeatherInputError,
)

__all__ = ["interpolate_weather", "WeatherSeries"]


class _ValidatedSeries(NamedTuple):
    records: tuple[HourlyWeather, ...]
    timestamps: tuple[datetime, ...]


def _to_utc(value: datetime, label: str = "Timestamp") -> datetime:
    """Validate and normalize a datetime to UTC."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise WeatherInputError(
            f"{label} must be a timezone-aware datetime."
        )

    return value.astimezone(timezone.utc)


def _validate_forecasts(
    forecasts: Sequence[HourlyWeather],
) -> _ValidatedSeries:
    """Validate records once and cache their UTC timestamps."""
    if isinstance(forecasts, (str, bytes)):
        raise WeatherInputError(
            "Forecasts must be a sequence of HourlyWeather records."
        )

    try:
        records = tuple(forecasts)
    except TypeError as exc:
        raise WeatherInputError(
            "Forecasts must be an iterable of HourlyWeather records."
        ) from exc

    timestamps: list[datetime] = []
    previous: datetime | None = None

    for index, record in enumerate(records):
        if not isinstance(record, HourlyWeather):
            raise WeatherInputError(
                f"Forecast at index {index} is not an HourlyWeather record."
            )

        timestamp = _to_utc(record.timestamp)

        if previous is not None and timestamp <= previous:
            raise WeatherInputError(
                "Forecast timestamps must be strictly increasing "
                f"(index {index})."
            )

        timestamps.append(timestamp)
        previous = timestamp

    return _ValidatedSeries(records, tuple(timestamps))


def _interpolate_wind(
    before: float | None,
    after: float | None,
    fraction: float,
) -> float | None:
    """Estimate wind speed only when both endpoint values are available."""
    if before is None or after is None:
        return None

    return before + (after - before) * fraction


class WeatherSeries:
    """
    Immutable-by-interface, pre-validated forecast series.

    Construct once and reuse .at() for multiple checkpoint lookups.
    Forecast records must be supplied in strictly increasing time order.
    """

    __slots__ = ("_records", "_timestamps")

    def __init__(self, forecasts: Sequence[HourlyWeather]) -> None:
        series = _validate_forecasts(forecasts)

        if not series.records:
            raise WeatherInputError(
                "At least one forecast record is required."
            )

        self._records: tuple[HourlyWeather, ...] = series.records
        self._timestamps: tuple[datetime, ...] = series.timestamps

    def __len__(self) -> int:
        return len(self._records)

    def __repr__(self) -> str:
        return (
            f"<WeatherSeries n={len(self)} "
            f"start={self._timestamps[0].isoformat()} "
            f"end={self._timestamps[-1].isoformat()}>"
        )

    def at(self, target_time: datetime) -> HourlyWeather:
        """
        Return weather at an exact forecast timestamp or estimate wind
        between two surrounding timestamps.

        Precipitation and snowfall accumulation values are preserved only
        for exact matches. For non-exact timestamps they are None because
        hourly totals do not establish the amount at an arbitrary instant.

        Extrapolation outside the forecast range is not allowed.
        """
        target = _to_utc(target_time, "Target time")
        index = bisect_left(self._timestamps, target)

        if (
            index < len(self._timestamps)
            and self._timestamps[index] == target
        ):
            return self._records[index]

        if index == 0 or index == len(self._records):
            raise WeatherInputError(
                f"Target time {target.isoformat()} is outside the "
                f"available forecast range "
                f"[{self._timestamps[0].isoformat()}, "
                f"{self._timestamps[-1].isoformat()}]."
            )

        before = self._records[index - 1]
        after = self._records[index]
        before_time = self._timestamps[index - 1]
        after_time = self._timestamps[index]

        span_seconds = (after_time - before_time).total_seconds()
        elapsed_seconds = (target - before_time).total_seconds()

        if span_seconds <= 0:
            raise WeatherInputError(
                "Forecast timestamps must have a positive interval."
            )

        fraction = elapsed_seconds / span_seconds

        return HourlyWeather(
            timestamp=target,
            wind_mph=_interpolate_wind(
                before.wind_mph,
                after.wind_mph,
                fraction,
            ),
            precipitation_inches=None,
            snowfall_inches=None,
        )


def interpolate_weather(
    forecasts: Sequence[HourlyWeather],
    target_time: datetime,
) -> HourlyWeather:
    """
    Convenience wrapper for a single lookup.

    For repeated lookups against the same forecasts, construct a
    WeatherSeries once and call .at() for each target time.
    """
    return WeatherSeries(forecasts).at(target_time)
