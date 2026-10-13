
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from apps.routing.services.weather.base import (
    HourlyWeather,
    WeatherInputError,
)
from apps.routing.services.weather.interpolation import (
    WeatherSeries,
    interpolate_weather,
)


START = datetime(2026, 10, 13, 10, tzinfo=timezone.utc)


def make_weather(
    hour: int,
    *,
    wind: float | None = 20.0,
    rain: float | None = 0.2,
    snow: float | None = 0.0,
) -> HourlyWeather:
    return HourlyWeather(
        timestamp=START + timedelta(hours=hour),
        wind_mph=wind,
        precipitation_inches=rain,
        snowfall_inches=snow,
    )


@pytest.fixture
def forecasts():
    return [
        make_weather(0, wind=20.0, rain=0.2, snow=0.0),
        make_weather(1, wind=30.0, rain=0.4, snow=0.2),
        make_weather(2, wind=40.0, rain=0.6, snow=0.4),
    ]


def test_exact_timestamp_returns_original_record(forecasts):
    series = WeatherSeries(forecasts)

    result = series.at(START + timedelta(hours=1))

    assert result is forecasts[1]
    assert result.wind_mph == 30.0
    assert result.precipitation_inches == 0.4
    assert result.snowfall_inches == 0.2


def test_midpoint_interpolates_wind(forecasts):
    result = interpolate_weather(
        forecasts,
        START + timedelta(minutes=30),
    )

    assert result.wind_mph == pytest.approx(25.0)


def test_non_exact_timestamp_does_not_interpolate_accumulations(
    forecasts,
):
    result = interpolate_weather(
        forecasts,
        START + timedelta(minutes=30),
    )

    assert result.precipitation_inches is None
    assert result.snowfall_inches is None


def test_missing_wind_remains_none():
    forecasts = [
        make_weather(0, wind=None),
        make_weather(1, wind=30.0),
    ]

    result = interpolate_weather(
        forecasts,
        START + timedelta(minutes=30),
    )

    assert result.wind_mph is None


def test_missing_wind_at_second_endpoint_remains_none():
    forecasts = [
        make_weather(0, wind=20.0),
        make_weather(1, wind=None),
    ]

    result = interpolate_weather(
        forecasts,
        START + timedelta(minutes=30),
    )

    assert result.wind_mph is None


def test_empty_forecasts_are_rejected():
    with pytest.raises(WeatherInputError, match="At least one"):
        WeatherSeries([])


@pytest.mark.parametrize(
    "target",
    [
        START - timedelta(minutes=1),
        START + timedelta(hours=2, minutes=1),
    ],
)
def test_out_of_range_target_is_rejected(forecasts, target):
    with pytest.raises(WeatherInputError, match="outside"):
        interpolate_weather(forecasts, target)


def test_naive_target_is_rejected(forecasts):
    target = datetime(2026, 10, 13, 10, 30)

    with pytest.raises(WeatherInputError, match="timezone-aware"):
        interpolate_weather(forecasts, target)


def test_naive_forecast_timestamp_is_rejected():
    forecast = Mock(
        spec=HourlyWeather,
        timestamp=datetime(2026, 10, 13, 10),
    )

    with pytest.raises(WeatherInputError, match="timezone-aware"):
        WeatherSeries([forecast])


@pytest.mark.parametrize(
    "records",
    [
        [make_weather(1), make_weather(0)],
        [make_weather(0), make_weather(0)],
    ],
)
def test_unsorted_or_duplicate_timestamps_are_rejected(records):
    with pytest.raises(
        WeatherInputError,
        match="strictly increasing",
    ):
        WeatherSeries(records)


def test_non_weather_record_is_rejected():
    with pytest.raises(WeatherInputError, match="HourlyWeather"):
        WeatherSeries([make_weather(0), "invalid"])


def test_utc_offset_is_normalized():
    local_timestamp = datetime(
        2026, 10, 13, 16, 0,
        tzinfo=timezone(timedelta(hours=5, minutes=30)),
    )

    forecasts = [
        make_weather(0, wind=20.0),
        make_weather(1, wind=30.0),
    ]

    result = interpolate_weather(forecasts, local_timestamp)

    assert result.timestamp == START + timedelta(minutes=30)
    assert result.wind_mph == pytest.approx(25.0)

    exact_local = datetime(
        2026, 10, 13, 15, 30,
        tzinfo=timezone(timedelta(hours=5, minutes=30)),
    )
    exact_result = interpolate_weather(forecasts, exact_local)
    assert exact_result.timestamp == START
    assert exact_result.wind_mph == pytest.approx(20.0)


def test_weather_series_supports_repeated_lookups(forecasts):
    series = WeatherSeries(forecasts)

    first = series.at(START + timedelta(minutes=15))
    second = series.at(START + timedelta(minutes=45))

    assert first.wind_mph == pytest.approx(22.5)
    assert second.wind_mph == pytest.approx(27.5)
    assert len(series) == 3


def test_single_record_only_allows_exact_timestamp():
    forecasts = [make_weather(0)]
    series = WeatherSeries(forecasts)

    assert series.at(START) is forecasts[0]

    with pytest.raises(WeatherInputError, match="outside"):
        series.at(START + timedelta(minutes=1))
