
"""Tests for the address geocoder adapter."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from geopy.exc import GeocoderRateLimited, GeocoderTimedOut

from apps.routing.services.routing.base import (
    RoutingInputError,
    RoutingProviderError,
)
from apps.routing.services.routing.geocoder import Geocoder


USER_AGENT = "truckersafe/1.0 (test@example.com)"


def make_geocoder(result=None, *, cache_size=256, min_interval=0):
    client = Mock()
    client.geocode.return_value = result
    geocoder = Geocoder(
        user_agent=USER_AGENT,
        client=client,
        cache_size=cache_size,
        min_interval_seconds=min_interval,
    )
    return geocoder, client


def location(latitude=41.8781, longitude=-87.6298):
    return SimpleNamespace(latitude=latitude, longitude=longitude)


def test_valid_address_returns_latitude_longitude():
    geocoder, client = make_geocoder(location())

    result = geocoder.geocode("Chicago, Illinois")

    assert result == (41.8781, -87.6298)
    client.geocode.assert_called_once()


def test_address_whitespace_is_normalized():
    geocoder, client = make_geocoder(location())

    geocoder.geocode("  Chicago   ,   Illinois  ")

    assert client.geocode.call_args.args[0] == "Chicago , Illinois"


@pytest.mark.parametrize("address", ["", " ", "\n\t", "a", "x" * 501, None, 123])
def test_invalid_address_raises_input_error(address):
    geocoder, client = make_geocoder(location())

    with pytest.raises(RoutingInputError):
        geocoder.geocode(address)

    client.geocode.assert_not_called()


def test_no_result_raises_provider_error():
    geocoder, _ = make_geocoder(None)

    with pytest.raises(RoutingProviderError, match="No coordinates found"):
        geocoder.geocode("Unknown Place")


@pytest.mark.parametrize(
    "exception",
    [
        GeocoderTimedOut("timeout"),
        GeocoderRateLimited("rate limited"),
    ],
)
def test_provider_errors_are_normalized(exception):
    geocoder, client = make_geocoder()
    client.geocode.side_effect = exception

    with pytest.raises(RoutingProviderError):
        geocoder.geocode("Chicago, Illinois")


@pytest.mark.parametrize(
    "latitude,longitude",
    [
        (float("nan"), 0),
        (0, float("inf")),
        (91, 0),
        (-91, 0),
        (0, 181),
        (0, -181),
        (None, 0),
        ("invalid", 0),
    ],
)
def test_invalid_coordinates_are_rejected(latitude, longitude):
    geocoder, _ = make_geocoder(location(latitude, longitude))

    with pytest.raises(RoutingProviderError):
        geocoder.geocode("Chicago, Illinois")


def test_cache_prevents_duplicate_provider_calls():
    geocoder, client = make_geocoder(location())

    first = geocoder.geocode("Chicago, Illinois")
    second = geocoder.geocode("Chicago, Illinois")

    assert first == second == (41.8781, -87.6298)
    client.geocode.assert_called_once()


def test_cache_is_disabled_when_size_is_zero():
    geocoder, client = make_geocoder(location(), cache_size=0)

    geocoder.geocode("Chicago, Illinois")
    geocoder.geocode("Chicago, Illinois")

    assert client.geocode.call_count == 2


def test_language_and_country_codes_are_forwarded():
    geocoder, client = make_geocoder(location())

    geocoder.geocode(
        "Vadodara, India",
        language="en",
        country_codes="IN,us",
    )

    kwargs = client.geocode.call_args.kwargs
    assert kwargs["language"] == "en"
    assert kwargs["country_codes"] == "in,us"


@pytest.mark.parametrize(
    "country_codes",
    ["i", "india", "in,,us", "1n", "in, usa", ""],
)
def test_invalid_country_codes_raise_input_error(country_codes):
    geocoder, client = make_geocoder(location())

    with pytest.raises(RoutingInputError):
        geocoder.geocode("Vadodara, India", country_codes=country_codes)

    client.geocode.assert_not_called()


@pytest.mark.parametrize("language", ["", " ", 123])
def test_invalid_language_raises_input_error(language):
    geocoder, client = make_geocoder(location())

    with pytest.raises(RoutingInputError):
        geocoder.geocode("Chicago, Illinois", language=language)

    client.geocode.assert_not_called()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"timeout": 0},
        {"timeout": -1},
        {"timeout": float("inf")},
        {"timeout": float("nan")},
        {"timeout": True},
        {"min_interval_seconds": -1},
        {"min_interval_seconds": float("nan")},
        {"min_interval_seconds": True},
        {"cache_size": -1},
        {"cache_size": True},
    ],
)
def test_invalid_constructor_arguments_raise_input_error(kwargs):
    with pytest.raises(RoutingInputError):
        Geocoder(user_agent=USER_AGENT, client=Mock(), **kwargs)


def test_falsy_injected_client_is_still_used():
    class FalsyClient:
        def __bool__(self):
            return False

        def geocode(self, query, **kwargs):
            return location()

    client = FalsyClient()
    geocoder = Geocoder(user_agent=USER_AGENT, client=client)

    assert geocoder.geocode("Chicago, Illinois") == (41.8781, -87.6298)


def test_invalid_user_agent_is_rejected():
    with pytest.raises(RoutingInputError):
        Geocoder(user_agent="short", client=Mock())


def test_cache_key_includes_country_and_language():
    geocoder, client = make_geocoder(location())

    geocoder.geocode("Springfield", country_codes="us", language="en")
    geocoder.geocode("Springfield", country_codes="in", language="en")

    assert client.geocode.call_count == 2


def test_geocoder_does_not_close_injected_client():
    client = Mock()
    geocoder = Geocoder(user_agent=USER_AGENT, client=client)

    geocoder.close()

    client.close.assert_not_called()
