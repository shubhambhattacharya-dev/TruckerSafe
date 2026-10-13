
import math

import pytest

from apps.routing.services.risk.engine import RiskBand
from apps.routing.services.risk.aggregation import aggregate_route_risk


def checkpoint(
    distance: float,
    band: RiskBand,
    *,
    incomplete_data: bool = False,
) -> dict:
    """Create a checkpoint using the aggregation input schema."""
    return {
        "cumulative_distance_miles": distance,
        "final_band": band.name,
        "incomplete_data": incomplete_data,
    }


def band_miles_total(result: dict) -> float:
    """Sum the miles assigned to all five risk bands."""
    return math.fsum(
        result[key]
        for key in (
            "low_mi",
            "moderate_mi",
            "high_mi",
            "severe_mi",
            "no_travel_mi",
        )
    )


def test_band_miles_sum_to_route_distance():
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        checkpoint(10, RiskBand.MODERATE),
        checkpoint(25, RiskBand.HIGH),
        checkpoint(40, RiskBand.LOW),
    ]

    result = aggregate_route_risk(
        checkpoints,
        route_distance_miles=40,
    )

    assert math.isclose(band_miles_total(result), 40)
    assert result["route_distance_mi"] == 40


def test_segment_uses_worse_endpoint_band():
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        checkpoint(10, RiskBand.SEVERE),
        checkpoint(20, RiskBand.MODERATE),
    ]

    result = aggregate_route_risk(checkpoints)

    # LOW -> SEVERE: 10 miles assigned to SEVERE.
    # SEVERE -> MODERATE: 10 miles assigned to SEVERE.
    assert result["severe_mi"] == 20
    assert result["no_travel_mi"] == 0
    assert result["high_mi"] == 0
    assert result["moderate_mi"] == 0
    assert result["low_mi"] == 0


def test_distance_weighted_average_score():
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        checkpoint(10, RiskBand.LOW),
        checkpoint(30, RiskBand.HIGH),
    ]

    result = aggregate_route_risk(checkpoints)

    # First segment: 10 miles * LOW score (1).
    # Second segment: 20 miles * HIGH score (3).
    # Average = (10 * 1 + 20 * 3) / 30 = 7/3.
    assert result["avg_score"] == pytest.approx(7 / 3)


def test_no_travel_band_is_counted_correctly():
    checkpoints = [
        checkpoint(0, RiskBand.HIGH),
        checkpoint(5, RiskBand.NO_TRAVEL),
        checkpoint(15, RiskBand.LOW),
    ]

    result = aggregate_route_risk(checkpoints)

    # Both segments touch a NO_TRAVEL checkpoint.
    assert result["no_travel_mi"] == 15
    assert band_miles_total(result) == pytest.approx(15)


def test_incomplete_data_is_propagated():
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        checkpoint(10, RiskBand.MODERATE, incomplete_data=True),
    ]

    result = aggregate_route_risk(checkpoints)

    assert result["incomplete_data"] is True


def test_complete_data_returns_false():
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        checkpoint(10, RiskBand.MODERATE),
    ]

    result = aggregate_route_risk(checkpoints)

    assert result["incomplete_data"] is False


def test_zero_length_segment_adds_no_miles():
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        checkpoint(0, RiskBand.SEVERE),
        checkpoint(10, RiskBand.MODERATE),
    ]

    result = aggregate_route_risk(checkpoints)

    assert result["route_distance_mi"] == 10
    assert result["severe_mi"] == 10
    assert band_miles_total(result) == pytest.approx(10)


def test_tiny_nonzero_start_distance_is_normalized():
    checkpoints = [
        checkpoint(5e-10, RiskBand.LOW),
        checkpoint(10, RiskBand.MODERATE),
    ]

    result = aggregate_route_risk(checkpoints)

    assert result["route_distance_mi"] == 10
    assert band_miles_total(result) == pytest.approx(10)


def test_rejects_non_monotonic_distances():
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        checkpoint(10, RiskBand.MODERATE),
        checkpoint(8, RiskBand.HIGH),
    ]

    with pytest.raises(ValueError, match="non-decreasing"):
        aggregate_route_risk(checkpoints)


def test_rejects_nonzero_start_distance():
    checkpoints = [
        checkpoint(1, RiskBand.LOW),
        checkpoint(10, RiskBand.HIGH),
    ]

    with pytest.raises(ValueError, match="must be zero"):
        aggregate_route_risk(checkpoints)


def test_rejects_mismatched_route_distance():
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        checkpoint(10, RiskBand.MODERATE),
    ]

    with pytest.raises(ValueError, match="does not match"):
        aggregate_route_risk(
            checkpoints,
            route_distance_miles=12,
        )


@pytest.mark.parametrize(
    "invalid_distance",
    [
        -1,
        float("nan"),
        float("inf"),
        True,
        "10",
    ],
)
def test_rejects_invalid_checkpoint_distance(invalid_distance):
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        checkpoint(invalid_distance, RiskBand.HIGH),
    ]

    with pytest.raises(ValueError):
        aggregate_route_risk(checkpoints)


@pytest.mark.parametrize(
    "invalid_route_distance",
    [
        -1,
        float("nan"),
        float("inf"),
        True,
        "10",
    ],
)
def test_rejects_invalid_route_distance(invalid_route_distance):
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        checkpoint(10, RiskBand.MODERATE),
    ]

    with pytest.raises(ValueError):
        aggregate_route_risk(
            checkpoints,
            route_distance_miles=invalid_route_distance,
        )


def test_rejects_unknown_risk_band():
    checkpoints = [
        checkpoint(0, RiskBand.LOW),
        {
            "cumulative_distance_miles": 10,
            "final_band": "UNKNOWN",
        },
    ]

    with pytest.raises(ValueError, match="Unknown risk band"):
        aggregate_route_risk(checkpoints)


def test_requires_at_least_two_checkpoints():
    with pytest.raises(ValueError, match="At least two"):
        aggregate_route_risk([
            checkpoint(0, RiskBand.LOW),
        ])


def test_empty_checkpoints_are_rejected():
    with pytest.raises(ValueError, match="At least two"):
        aggregate_route_risk([])
