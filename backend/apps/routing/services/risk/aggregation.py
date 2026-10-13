
from __future__ import annotations

import math
from numbers import Real
from typing import Any, Mapping, Sequence

from apps.routing.services.risk.engine import RiskBand


RISK_SCORE: dict[RiskBand, int] = {
    RiskBand.LOW: 1,
    RiskBand.MODERATE: 2,
    RiskBand.HIGH: 3,
    RiskBand.SEVERE: 4,
    RiskBand.NO_TRAVEL: 5,
}

BAND_MILE_KEYS: dict[RiskBand, str] = {
    RiskBand.LOW: "low_mi",
    RiskBand.MODERATE: "moderate_mi",
    RiskBand.HIGH: "high_mi",
    RiskBand.SEVERE: "severe_mi",
    RiskBand.NO_TRAVEL: "no_travel_mi",
}

_BAND_FIELDS = ("final_band", "risk_band")
_DISTANCE_FIELDS = ("cumulative_distance_miles", "distance_miles")

_MATCH_REL_TOL = 1e-6
_MATCH_ABS_TOL = 1e-6
_ZERO_ABS_TOL = 1e-9


def _get_first_present(
    checkpoint: Mapping[str, Any],
    fields: Sequence[str],
) -> Any:
    """Return the first non-None value among the specified fields."""
    for field in fields:
        value = checkpoint.get(field)
        if value is not None:
            return value
    return None


def _get_band(checkpoint: Mapping[str, Any]) -> RiskBand:
    """Extract and validate a checkpoint's final risk band."""
    value = _get_first_present(checkpoint, _BAND_FIELDS)

    if isinstance(value, RiskBand):
        return value

    if isinstance(value, str):
        try:
            return RiskBand[value.strip().upper()]
        except KeyError as exc:
            raise ValueError(f"Unknown risk band: {value!r}") from exc

    raise ValueError(
        "Each checkpoint must contain 'final_band' or 'risk_band'."
    )


def _to_finite_float(value: Any, field_name: str) -> float:
    """Convert a real numeric value to a finite float."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{field_name} must be numeric.")

    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(
            f"{field_name} must be finite and non-negative."
        ) from exc

    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be finite.")

    return number


def _get_distance_miles(
    checkpoint: Mapping[str, Any],
) -> float:
    """Extract cumulative distance in miles from a checkpoint."""
    value = _get_first_present(checkpoint, _DISTANCE_FIELDS)

    if value is None:
        raise ValueError(
            "Each checkpoint needs 'cumulative_distance_miles' "
            "or 'distance_miles'."
        )

    distance = _to_finite_float(value, "Checkpoint distance")

    if distance < 0:
        raise ValueError(
            "Checkpoint distance must be non-negative."
        )

    return distance


def _validate_route_distance(
    route_distance_miles: float,
    calculated_distance: float,
) -> None:
    """Ensure the supplied route distance matches checkpoint coverage."""
    route_distance = _to_finite_float(
        route_distance_miles,
        "route_distance_miles",
    )

    if route_distance < 0:
        raise ValueError(
            "route_distance_miles must be non-negative."
        )

    if not math.isclose(
        route_distance,
        calculated_distance,
        rel_tol=_MATCH_REL_TOL,
        abs_tol=_MATCH_ABS_TOL,
    ):
        raise ValueError(
            "Route distance does not match the final checkpoint distance."
        )


def aggregate_route_risk(
    checkpoints: Sequence[Mapping[str, Any]],
    *,
    route_distance_miles: float | None = None,
) -> dict[str, Any]:
    """
    Aggregate checkpoint risks into route-level statistics.

    Segment risk:
        The worse risk band of the two consecutive endpoints.

    Segment distance:
        Difference between consecutive cumulative distances.

    Average score:
        Distance-weighted mean of segment risk scores.

    Required checkpoint fields:
        - final_band or risk_band
        - cumulative_distance_miles or distance_miles

    Optional checkpoint field:
        - incomplete_data: truthy when data for that checkpoint is incomplete.

    Returns:
        low_mi, moderate_mi, high_mi, severe_mi, no_travel_mi,
        route_distance_mi, avg_score, incomplete_data.

    Assumptions:
        - Checkpoints are ordered along the route.
        - The first checkpoint represents distance zero.
        - The last checkpoint represents the end of the analyzed route.
    """
    if len(checkpoints) < 2:
        raise ValueError(
            "At least two checkpoints are required to aggregate a route."
        )

    bands = [_get_band(cp) for cp in checkpoints]
    distances = [_get_distance_miles(cp) for cp in checkpoints]

    # Validate the start, then normalize insignificant floating-point noise.
    if not math.isclose(
        distances[0],
        0.0,
        rel_tol=0.0,
        abs_tol=_ZERO_ABS_TOL,
    ):
        raise ValueError(
            "The first checkpoint's cumulative distance must be zero."
        )

    distances[0] = 0.0

    for index, (previous, current) in enumerate(
        zip(distances, distances[1:]),
        start=1,
    ):
        if current < previous:
            raise ValueError(
                "Cumulative checkpoint distances must be non-decreasing "
                f"(index {index}: {current} < {previous})."
            )

    total_distance = distances[-1]

    if route_distance_miles is not None:
        _validate_route_distance(
            route_distance_miles,
            total_distance,
        )

    miles_by_band: dict[str, float] = {
        key: 0.0 for key in BAND_MILE_KEYS.values()
    }

    weighted_score_total = 0.0

    for index, (start_band, end_band) in enumerate(
        zip(bands, bands[1:])
    ):
        segment_miles = distances[index + 1] - distances[index]

        if segment_miles == 0.0:
            continue

        # Choose the endpoint with the higher explicit risk score.
        segment_band = max(
            (start_band, end_band),
            key=RISK_SCORE.__getitem__,
        )

        miles_by_band[BAND_MILE_KEYS[segment_band]] += segment_miles
        weighted_score_total += (
            segment_miles * RISK_SCORE[segment_band]
        )

    avg_score = (
        weighted_score_total / total_distance
        if total_distance > 0.0
        else 0.0
    )

    incomplete_data = any(
        bool(checkpoint.get("incomplete_data", False))
        for checkpoint in checkpoints
    )

    # Every non-zero segment belongs to exactly one risk band.
    # This check catches unexpected accounting errors.
    band_miles_total = math.fsum(miles_by_band.values())

    if not math.isclose(
        band_miles_total,
        total_distance,
        rel_tol=_MATCH_REL_TOL,
        abs_tol=_MATCH_ABS_TOL,
    ):
        raise ArithmeticError(
            "Risk-band miles do not sum to the analyzed route distance."
        )

    return {
        **miles_by_band,
        "route_distance_mi": total_distance,
        "avg_score": avg_score,
        "incomplete_data": incomplete_data,
    }
