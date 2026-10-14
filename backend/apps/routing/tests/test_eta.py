
from datetime import datetime, timedelta, timezone

import pytest

from apps.routing.services.geo.haversine import haversine_distance
from apps.routing.services.routing.base import RoutingInputError
from apps.routing.services.routing.eta import (
    RouteProjector,
    estimate_checkpoint_etas,
)

METERS_PER_MILE = 1609.344


def make_route(duration_seconds=3600.0):
    """Create a straight, approximately 69-mile test route."""
    geometry = [
        [0.0, 0.0],  # longitude, latitude
        [1.0, 0.0],
    ]

    distance_miles = haversine_distance(
        0.0, 0.0, 0.0, 1.0
    )

    return {
        "geometry": geometry,
        "distance_meters": distance_miles * METERS_PER_MILE,
        "duration_seconds": duration_seconds,
    }


def departure():
    return datetime(2026, 10, 14, 8, 0, tzinfo=timezone.utc)


def test_route_projector_initializes_without_slots_error():
    projector = RouteProjector(make_route())

    assert projector.duration_seconds == 3600.0
    assert projector.total_miles > 0
    assert len(projector) == 2


def test_start_checkpoint_has_zero_distance_and_departure_eta():
    results = estimate_checkpoint_etas(
        make_route(),
        departure(),
        [(0.0, 0.0)],
    )

    assert results[0]["distance_miles"] == pytest.approx(0.0)
    assert results[0]["arrival_time"] == departure()


def test_midpoint_checkpoint_gets_half_route_duration():
    results = estimate_checkpoint_etas(
        make_route(),
        departure(),
        [(0.0, 0.5)],
    )

    assert results[0]["distance_miles"] == pytest.approx(
        RouteProjector(make_route()).total_miles / 2,
        abs=0.01,
    )
    assert results[0]["arrival_time"] == (
        departure() + timedelta(minutes=30)
    )


def test_destination_checkpoint_gets_full_route_duration():
    results = estimate_checkpoint_etas(
        make_route(),
        departure(),
        [(0.0, 1.0)],
    )

    assert results[0]["distance_miles"] == pytest.approx(
        RouteProjector(make_route()).total_miles
    )
    assert results[0]["arrival_time"] == (
        departure() + timedelta(hours=1)
    )


def test_results_are_timezone_aware_utc():
    local_departure = datetime(
        2026, 10, 14, 13, 30,
        tzinfo=timezone(timedelta(hours=5, minutes=30)),
    )

    results = estimate_checkpoint_etas(
        make_route(),
        local_departure,
        [(0.0, 0.5)],
    )

    eta = results[0]["arrival_time"]

    assert eta.tzinfo == timezone.utc
    assert eta == datetime(
        2026, 10, 14, 8, 30, tzinfo=timezone.utc
    )


def test_naive_departure_time_is_rejected():
    naive_time = datetime(2026, 10, 14, 8, 0)

    with pytest.raises(RoutingInputError, match="timezone"):
        estimate_checkpoint_etas(
            make_route(),
            naive_time,
            [(0.0, 0.5)],
        )


@pytest.mark.parametrize("duration", [0, -1, float("inf"), float("nan")])
def test_invalid_route_duration_is_rejected(duration):
    with pytest.raises(RoutingInputError):
        RouteProjector(make_route(duration_seconds=duration))


@pytest.mark.parametrize("checkpoint", [
    (91.0, 0.5),
    (0.0, 181.0),
    (float("nan"), 0.5),
    (True, 0.5),
    (0.0,),
])
def test_invalid_checkpoint_is_rejected(checkpoint):
    with pytest.raises(RoutingInputError):
        estimate_checkpoint_etas(
            make_route(),
            departure(),
            [checkpoint],
        )


def test_checkpoint_far_from_route_is_rejected():
    with pytest.raises(RoutingInputError, match="from the route"):
        estimate_checkpoint_etas(
            make_route(),
            departure(),
            [(5.0, 0.5)],
        )


def test_out_of_order_checkpoints_are_rejected():
    with pytest.raises(RoutingInputError, match="out of route order"):
        estimate_checkpoint_etas(
            make_route(),
            departure(),
            [
                (0.0, 0.8),
                (0.0, 0.2),
            ],
        )


def test_empty_checkpoints_are_rejected():
    with pytest.raises(RoutingInputError, match="non-empty"):
        estimate_checkpoint_etas(
            make_route(),
            departure(),
            [],
        )


def test_geometry_distance_mismatch_is_rejected():
    route = make_route()
    route["distance_meters"] *= 2

    with pytest.raises(RoutingInputError, match="geometry totals"):
        RouteProjector(route)


def test_duplicate_route_vertices_are_supported():
    route = make_route()
    route["geometry"] = [
        [0.0, 0.0],
        [0.0, 0.0],
        [1.0, 0.0],
    ]

    projector = RouteProjector(route)

    assert projector.total_miles > 0


def test_checkpoints_return_in_input_order():
    results = estimate_checkpoint_etas(
        make_route(),
        departure(),
        [
            (0.0, 0.0),
            (0.0, 0.25),
            (0.0, 0.5),
            (0.0, 1.0),
        ],
    )

    distances = [item["distance_miles"] for item in results]
    times = [item["arrival_time"] for item in results]

    assert distances == sorted(distances)
    assert times == sorted(times)
    assert len(results) == 4
