
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
import requests

from apps.routing.services.weather.base import (
    HourlyWeather,
    WeatherInputError,
    WeatherProviderError,
)
from apps.routing.services.weather.open_meteo_adapter import (
    OpenMeteoAdapter,
)


START = datetime(2026, 10, 13, 10, tzinfo=timezone.utc)
END = START + timedelta(hours=2)


def make_payload():
    return {
        "hourly": {
            "time": [
                "2026-10-13T10:00",
                "2026-10-13T11:00",
                "2026-10-13T12:00",
            ],
            "wind_speed_10m": [10.0, 25.0, 40.0],
            "precipitation": [0.0, 0.1, 0.3],
            "snowfall": [0.0, 0.0, 0.2],
        }
    }


def make_response(payload=None, status_code=200):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = (
        make_payload() if payload is None else payload
    )
    response.raise_for_status.side_effect = (
        requests.HTTPError(f"HTTP {status_code}")
        if status_code >= 400
        else None
    )
    return response


@pytest.fixture
def session():
    mock_session = Mock(spec=requests.Session)
    mock_session.headers = {}
    return mock_session


@pytest.fixture
def adapter(session):
    return OpenMeteoAdapter(
        session=session,
        max_retries=0,
    )


def test_successful_forecast_returns_hourly_weather(adapter, session):
    session.get.return_value = make_response()

    records = adapter.get_hourly_forecast(
        40.0, -75.0, START, END
    )

    assert len(records) == 3
    assert all(isinstance(item, HourlyWeather) for item in records)
    assert records[0].wind_mph == 10.0
    assert records[1].precipitation_inches == 0.1
    assert records[2].snowfall_inches == 0.2
    assert records[0].timestamp == START
    assert records[-1].timestamp == END


def test_request_uses_expected_parameters(adapter, session):
    session.get.return_value = make_response()

    adapter.get_hourly_forecast(40.0, -75.0, START, END)

    kwargs = session.get.call_args.kwargs
    params = kwargs["params"]

    assert kwargs["timeout"] == adapter.timeout
    assert params["latitude"] == 40.0
    assert params["longitude"] == -75.0
    assert params["wind_speed_unit"] == "mph"
    assert params["precipitation_unit"] == "inch"
    assert params["timezone"] == "UTC"
    assert params["hourly"] == (
        "wind_speed_10m,precipitation,snowfall"
    )


def test_forecast_filters_records_to_requested_window(adapter, session):
    session.get.return_value = make_response()

    start = START + timedelta(minutes=30)
    end = START + timedelta(hours=1, minutes=30)

    records = adapter.get_hourly_forecast(
        40.0, -75.0, start, end
    )

    assert len(records) == 1
    assert records[0].timestamp == START + timedelta(hours=1)


def test_missing_measurements_remain_none(adapter, session):
    payload = make_payload()
    payload["hourly"]["wind_speed_10m"][0] = None
    payload["hourly"]["precipitation"][1] = None
    payload["hourly"]["snowfall"][2] = None
    session.get.return_value = make_response(payload)

    records = adapter.get_hourly_forecast(
        40.0, -75.0, START, END
    )

    assert records[0].wind_mph is None
    assert records[1].precipitation_inches is None
    assert records[2].snowfall_inches is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("wind_speed_10m", -1),
        ("wind_speed_10m", float("nan")),
        ("precipitation", float("inf")),
        ("snowfall", True),
        ("precipitation", "invalid"),
    ],
)
def test_invalid_measurements_raise_provider_error(
    adapter, session, field, value
):
    payload = make_payload()
    payload["hourly"][field][0] = value
    session.get.return_value = make_response(payload)

    with pytest.raises(WeatherProviderError):
        adapter.get_hourly_forecast(
            40.0, -75.0, START, END
        )


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {},
        {"hourly": []},
        {"hourly": {"time": []}},
        {
            "hourly": {
                "time": ["2026-10-13T10:00"],
                "wind_speed_10m": [],
                "precipitation": [0.0],
                "snowfall": [0.0],
            }
        },
    ],
)
def test_malformed_response_raises_provider_error(
    adapter, session, payload
):
    session.get.return_value = make_response(payload)

    with pytest.raises(WeatherProviderError):
        adapter.get_hourly_forecast(
            40.0, -75.0, START, END
        )


def test_malformed_timestamp_raises_provider_error(adapter, session):
    payload = make_payload()
    payload["hourly"]["time"][0] = "not-a-timestamp"
    session.get.return_value = make_response(payload)

    with pytest.raises(WeatherProviderError, match="malformed"):
        adapter.get_hourly_forecast(
            40.0, -75.0, START, END
        )


def test_duplicate_timestamps_are_rejected(adapter, session):
    payload = make_payload()
    payload["hourly"]["time"][1] = payload["hourly"]["time"][0]
    session.get.return_value = make_response(payload)

    with pytest.raises(WeatherProviderError, match="increasing"):
        adapter.get_hourly_forecast(
            40.0, -75.0, START, END
        )


@pytest.mark.parametrize(
    "latitude,longitude",
    [
        (91, 0),
        (-91, 0),
        (0, 181),
        (0, -181),
        (float("nan"), 0),
        (0, float("inf")),
    ],
)
def test_invalid_coordinates_are_rejected_without_request(
    adapter, session, latitude, longitude
):
    with pytest.raises(WeatherInputError):
        adapter.get_hourly_forecast(
            latitude, longitude, START, END
        )

    session.get.assert_not_called()


def test_http_error_becomes_provider_error(adapter, session):
    session.get.return_value = make_response(status_code=503)

    with pytest.raises(WeatherProviderError, match="503"):
        adapter.get_hourly_forecast(
            40.0, -75.0, START, END
        )


def test_timeout_becomes_provider_error(adapter, session):
    session.get.side_effect = requests.Timeout("timed out")

    with pytest.raises(WeatherProviderError, match="timed out"):
        adapter.get_hourly_forecast(
            40.0, -75.0, START, END
        )


def test_network_error_becomes_provider_error(adapter, session):
    session.get.side_effect = requests.ConnectionError("offline")

    with pytest.raises(WeatherProviderError, match="network request"):
        adapter.get_hourly_forecast(
            40.0, -75.0, START, END
        )


def test_invalid_json_becomes_provider_error(adapter, session):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.side_effect = ValueError("invalid JSON")
    session.get.return_value = response

    with pytest.raises(WeatherProviderError, match="invalid JSON"):
        adapter.get_hourly_forecast(
            40.0, -75.0, START, END
        )


def test_caller_owned_session_is_not_closed(session):
    adapter = OpenMeteoAdapter(session=session, max_retries=0)

    adapter.close()

    session.close.assert_not_called()


def test_invalid_timeout_is_rejected():
    for timeout in (0, -1, float("inf"), float("nan"), True):
        with pytest.raises(ValueError):
            OpenMeteoAdapter(timeout=timeout)


def test_invalid_retry_count_is_rejected():
    for retries in (-1, 1.5, True):
        with pytest.raises(ValueError):
            OpenMeteoAdapter(max_retries=retries)


def test_session_user_agent_is_configured(session):
    OpenMeteoAdapter(session=session, max_retries=0)
    assert session.headers.get("User-Agent") == "truckersafe-weather/1.0"


def test_adapter_accepts_session_without_headers():
    bare_mock_session = Mock(spec=requests.Session)
    adapter = OpenMeteoAdapter(session=bare_mock_session, max_retries=0)
    assert adapter._session is bare_mock_session

