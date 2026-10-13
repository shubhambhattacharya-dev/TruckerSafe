
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Real
from typing import Any, Final


# Ranking fields: lower values are better.
NO_TRAVEL_MI: Final = "no_travel_mi"
SEVERE_MI: Final = "severe_mi"
HIGH_MI: Final = "high_mi"
AVG_SCORE: Final = "avg_score"
DURATION_MIN: Final = "duration_min"

_RANK_FIELDS: Final[tuple[str, ...]] = (
    NO_TRAVEL_MI,
    SEVERE_MI,
    HIGH_MI,
    AVG_SCORE,
    DURATION_MIN,
)

__all__ = [
    "is_disqualified",
    "rank_route",
    "prepare_ranking",
]


def _get_finite_number(
    plan: Mapping[str, Any],
    field: str,
) -> float:
    """Return a validated, finite, non-negative numeric field."""
    value = plan.get(field)

    # bool is a subclass of int, so reject it explicitly.
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{field!r} must be numeric.")

    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(
            f"{field!r} must be a finite number."
        ) from exc

    if not math.isfinite(number):
        raise ValueError(f"{field!r} must be finite.")

    if number < 0:
        raise ValueError(f"{field!r} cannot be negative.")

    return number


def _extract_rank_values(
    plan: Mapping[str, Any],
) -> tuple[float, ...]:
    """Extract ranking fields in the required priority order."""
    return tuple(
        _get_finite_number(plan, field)
        for field in _RANK_FIELDS
    )


def is_disqualified(plan: Mapping[str, Any]) -> bool:
    """
    Return True when the route contains any NO_TRAVEL miles.
    """
    no_travel_miles = _get_finite_number(
        plan,
        NO_TRAVEL_MI,
    )
    return no_travel_miles > 0.0


def _rank_key_from_values(
    values: tuple[float, ...],
) -> tuple[int, tuple[float, ...]]:
    """
    Build the lexicographic sort key from validated values.

    Qualified routes:     group 0
    Disqualified routes:  group 1
    """
    disqualified = values[0] > 0.0
    return (int(disqualified), values)


def rank_route(
    plan: Mapping[str, Any],
) -> tuple[int, tuple[float, ...]]:
    """
    Return a sort key for Python's ascending sorted() function.

    Priority:
        1. Qualified routes before disqualified routes.
        2. Fewer NO_TRAVEL miles.
        3. Fewer SEVERE miles.
        4. Fewer HIGH-risk miles.
        5. Lower average risk score.
        6. Shorter duration.
    """
    values = _extract_rank_values(plan)
    return _rank_key_from_values(values)


def prepare_ranking(
    plans: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """
    Return copied route plans sorted from best to worst.

    Adds:
        rank: 1-based position.
        disqualified: whether NO_TRAVEL miles are greater than zero.

    Original plan dictionaries are not modified.
    """
    validated_plans = [
        (plan, _extract_rank_values(plan))
        for plan in plans
    ]

    # Python's sort is stable: equal keys retain their input order.
    validated_plans.sort(
        key=lambda item: _rank_key_from_values(item[1])
    )

    results: list[dict[str, Any]] = []

    for rank, (plan, values) in enumerate(
        validated_plans,
        start=1,
    ):
        result = dict(plan)
        result["rank"] = rank
        result["disqualified"] = values[0] > 0.0
        results.append(result)

    return results
