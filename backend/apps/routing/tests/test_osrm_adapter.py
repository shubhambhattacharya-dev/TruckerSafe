
from unittest.mock import Mock, patch

import pytest
import requests

from apps.routing.services.routing.base import (
    RoutingInputError,
    RoutingProviderError,
)
from apps.routing.services.routing.osrm_adapter import OSRMAdapter


@pytest.fixture
def adapter():
    instance = OSRMAdapter()
    yield instance
    instance.close()


def make_osrm_response(routes=None, code="Ok", message=None):
    payload = {
        "code": code,
        "routes": routes if routes is not None else [
            {
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [72.50, 22.30],
                        [72.60, 22.40],
                        [72.70, 22.50],
                    ],
                },
                "distance": 125000,
                "duration": 7200,
            }
        ],
    }

    if message is not None:
        payload["message"] = message

    response = Mock()
    response.status_code = 200
    response.raise_for_status.return_value = None
    response.json.return_value = payload
    return response


@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_returns_normalized_route(mock_get, adapter):
    mock_get.return_value = make_osrm_response()

    routes = adapter.get_routes(
        (22.30, 72.50),
        (22.50, 72.70),
        alternatives=3,
    )

    assert len(routes) == 1
    assert routes[0]["geometry"] == [
        [72.50, 22.30],
        [72.60, 22.40],
        [72.70, 22.50],
    ]
    assert routes[0]["distance_meters"] == 125000.0
    assert routes[0]["duration_seconds"] == 7200.0
    assert isinstance(routes[0]["distance_meters"], float)
    assert isinstance(routes[0]["duration_seconds"], float)


@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_requests_alternatives_and_full_geometry(mock_get, adapter):
    mock_get.return_value = make_osrm_response()

    adapter.get_routes(
        (22.30, 72.50),
        (22.50, 72.70),
        alternatives=3,
    )

    _, kwargs = mock_get.call_args

    # OSRM counts EXTRA routes beyond the primary; the adapter's public
    # contract counts TOTAL routes, so 3 total routes -> alternatives=2.
    assert kwargs["params"]["alternatives"] == 2
    assert kwargs["params"]["overview"] == "full"
    assert kwargs["params"]["geometries"] == "geojson"
    assert kwargs["params"]["steps"] == "false"
    assert kwargs["timeout"] == 15.0


@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_uses_osrm_longitude_latitude_order(mock_get, adapter):
    mock_get.return_value = make_osrm_response()

    adapter.get_routes((22.30, 72.50), (22.50, 72.70))

    url = mock_get.call_args.args[0]

    assert "/72.5,22.3;72.7,22.5" in url


@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_accepts_fewer_routes_than_requested(mock_get, adapter):
    mock_get.return_value = make_osrm_response()

    routes = adapter.get_routes(
        (22.30, 72.50),
        (22.50, 72.70),
        alternatives=3,
    )

    # OSRM may return fewer alternatives than requested.
    assert len(routes) == 1


@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_rejects_osrm_error_response(mock_get, adapter):
    mock_get.return_value = make_osrm_response(
        routes=[],
        code="NoRoute",
        message="No route found",
    )

    with pytest.raises(
        RoutingProviderError,
        match="No route found",
    ):
        adapter.get_routes(
            (22.30, 72.50),
            (22.50, 72.70),
        )



@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_rejects_empty_routes(mock_get, adapter):
    mock_get.return_value = make_osrm_response(routes=[])

    with pytest.raises(RoutingProviderError, match="no routes"):
        adapter.get_routes((22.30, 72.50), (22.50, 72.70))


@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_handles_timeout(mock_get, adapter):
    mock_get.side_effect = requests.Timeout("timeout")

    with pytest.raises(RoutingProviderError, match="timed out"):
        adapter.get_routes((22.30, 72.50), (22.50, 72.70))


@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_handles_http_failure(mock_get, adapter):
    response = Mock()
    response.status_code = 503
    response.raise_for_status.side_effect = requests.HTTPError(
        "Service unavailable"
    )
    mock_get.return_value = response

    with pytest.raises(RoutingProviderError):
        adapter.get_routes((22.30, 72.50), (22.50, 72.70))


@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_handles_invalid_json(mock_get, adapter):
    response = Mock()
    response.status_code = 200
    response.raise_for_status.return_value = None
    response.json.side_effect = ValueError("invalid JSON")
    mock_get.return_value = response

    with pytest.raises(RoutingProviderError, match="invalid JSON"):
        adapter.get_routes((22.30, 72.50), (22.50, 72.70))


@pytest.mark.parametrize(
    "distance",
    [-1, float("nan"), float("inf"), True, "125000", None],
)
@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_rejects_invalid_distance(mock_get, adapter, distance):
    payload = make_osrm_response().json.return_value
    payload["routes"][0]["distance"] = distance
    mock_get.return_value = make_osrm_response(routes=payload["routes"])

    with pytest.raises(RoutingProviderError, match="distance"):
        adapter.get_routes((22.30, 72.50), (22.50, 72.70))


@pytest.mark.parametrize(
    "duration",
    [-1, float("nan"), float("inf"), True, "7200", None],
)
@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_rejects_invalid_duration(mock_get, adapter, duration):
    payload = make_osrm_response().json.return_value
    payload["routes"][0]["duration"] = duration
    mock_get.return_value = make_osrm_response(routes=payload["routes"])

    with pytest.raises(RoutingProviderError, match="duration"):
        adapter.get_routes((22.30, 72.50), (22.50, 72.70))


@pytest.mark.parametrize(
    "coordinates",
    [
        [[72.50, 22.30]],
        [[72.50]],
        [[float("nan"), 22.30], [72.60, 22.40]],
        [[181, 22.30], [72.60, 22.40]],
        [["72.50", 22.30], [72.60, 22.40]],
    ],
)
@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_rejects_invalid_geometry(mock_get, adapter, coordinates):
    route = {
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates,
        },
        "distance": 1000,
        "duration": 100,
    }
    mock_get.return_value = make_osrm_response(routes=[route])

    with pytest.raises(RoutingProviderError):
        adapter.get_routes((22.30, 72.50), (22.50, 72.70))


def test_rejects_identical_coordinates(adapter):
    with pytest.raises(RoutingInputError, match="different"):
        adapter.get_routes((22.30, 72.50), (22.30, 72.50))


def test_rejects_invalid_timeout():
    for timeout in (0, -1, float("inf"), float("nan"), True):
        with pytest.raises(ValueError):
            OSRMAdapter(timeout=timeout)


def test_rejects_empty_base_url():
    with pytest.raises(ValueError):
        OSRMAdapter(base_url="   ")


@patch("apps.routing.services.routing.osrm_adapter.requests.Session.get")
def test_adapter_cannot_be_used_after_close(mock_get, adapter):
    adapter.close()

    with pytest.raises(RuntimeError, match="closed"):
        adapter.get_routes((22.30, 72.50), (22.50, 72.70))

    mock_get.assert_not_called()
