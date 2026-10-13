
from datetime import datetime, timedelta, timezone

import pytest

from apps.routing.services.weather.base import (
    MAX_FORECAST_HOURS,
    MIN_FORECAST_HOURS,
    HourlyWeather,
    WeatherInputError,
    WeatherProvider,
)


def make_datetime(hours: int = 0) -> datetime:
    return datetime(2026, 10, 13, tzinfo=timezone.utc) + timedelta(
        hours=hours
    )


def test_valid_hourly_weather_record():
    weather = HourlyWeather(
        timestamp=make_datetime(),
        wind_mph=25.0,
        precipitation_inches=0.1,
        snowfall_inches=0.0,
    )

    assert weather.wind_mph == 25.0
    assert weather.precipitation_inches == 0.1
    assert weather.snowfall_inches == 0.0


@pytest.mark.parametrize(
    "field,value",
    [
        ("wind_mph", -1),
        ("precipitation_inches", -0.1),
        ("snowfall_inches", -0.1),
        ("wind_mph", float("nan")),
        ("wind_mph", float("inf")),
        ("precipitation_inches", True),
    ],
)
def test_invalid_weather_measurements_are_rejected(field, value):
    values = {
        "timestamp": make_datetime(),
        "wind_mph": 10.0,
        "precipitation_inches": 0.0,
        "snowfall_inches": 0.0,
    }
    values[field] = value

    with pytest.raises(ValueError):
        HourlyWeather(**values)


def test_missing_measurements_remain_none():
    weather = HourlyWeather(
        timestamp=make_datetime(),
        wind_mph=None,
        precipitation_inches=None,
        snowfall_inches=None,
    )

    assert weather.wind_mph is None
    assert weather.precipitation_inches is None
    assert weather.snowfall_inches is None


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        HourlyWeather(
            timestamp=datetime(2026, 10, 13),
            wind_mph=10,
            precipitation_inches=0,
            snowfall_inches=0,
        )


class DummyWeatherProvider(WeatherProvider):
    def get_hourly_forecast(
        self, latitude, longitude, start, end
    ):
        self._validate_request(latitude, longitude, start, end)
        return []


@pytest.mark.parametrize(
    "latitude,longitude",
    [
        (-90, -180),
        (90, 180),
        (0, 0),
    ],
)
def test_valid_coordinate_boundaries(latitude, longitude):
    provider = DummyWeatherProvider()

    provider._validate_coordinates(latitude, longitude)


@pytest.mark.parametrize(
    "latitude,longitude",
    [
        (-90.1, 0),
        (90.1, 0),
        (0, -180.1),
        (0, 180.1),
        (float("nan"), 0),
        (0, float("inf")),
        (True, 0),
    ],
)
def test_invalid_coordinates_are_rejected(latitude, longitude):
    provider = DummyWeatherProvider()

    with pytest.raises(WeatherInputError):
        provider._validate_coordinates(latitude, longitude)


def test_forecast_window_accepts_minimum_and_maximum():
    provider = DummyWeatherProvider()
    start = make_datetime()

    provider._validate_window(
        start, start + timedelta(hours=MIN_FORECAST_HOURS)
    )
    provider._validate_window(
        start, start + timedelta(hours=MAX_FORECAST_HOURS)
    )


@pytest.mark.parametrize(
    "hours",
    [
        0,
        MIN_FORECAST_HOURS - 0.5,
        MAX_FORECAST_HOURS + 1,
    ],
)
def test_invalid_forecast_window_is_rejected(hours):
    provider = DummyWeatherProvider()
    start = make_datetime()

    with pytest.raises(WeatherInputError):
        provider._validate_window(
            start, start + timedelta(hours=hours)
        )


def test_end_before_start_is_rejected():
    provider = DummyWeatherProvider()
    start = make_datetime()

    with pytest.raises(WeatherInputError, match="on or after"):
        provider._validate_window(
            start, start - timedelta(hours=1)
        )


def test_provider_must_implement_forecast_method():
    with pytest.raises(TypeError):
        WeatherProvider()
