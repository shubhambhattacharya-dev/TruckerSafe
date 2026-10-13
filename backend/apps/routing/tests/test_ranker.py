
import math

import pytest

from apps.routing.services.recommend.ranker import (
    is_disqualified,
    rank_route,
    prepare_ranking,
)


def make_plan(
    *,
    name="Route",
    no_travel_mi=0,
    severe_mi=0,
    high_mi=0,
    avg_score=1,
    duration_min=100,
):
    return {
        "name": name,
        "no_travel_mi": no_travel_mi,
        "severe_mi": severe_mi,
        "high_mi": high_mi,
        "avg_score": avg_score,
        "duration_min": duration_min,
    }




def test_route_without_no_travel_miles_is_qualified():
    plan = make_plan(no_travel_mi=0)

    assert is_disqualified(plan) is False


def test_route_with_no_travel_miles_is_disqualified():
    plan = make_plan(no_travel_mi=1)

    assert is_disqualified(plan) is True


def test_any_positive_no_travel_distance_disqualifies_route():
    plan = make_plan(no_travel_mi=0.001)

    assert is_disqualified(plan) is True





def test_qualified_route_ranks_before_disqualified_route():
    safe = make_plan(name="Safe", no_travel_mi=0)
    unsafe = make_plan(name="Unsafe", no_travel_mi=5)

    ranked = prepare_ranking([unsafe, safe])

    assert [p["name"] for p in ranked] == ["Safe", "Unsafe"]


def test_fewer_severe_miles_wins_before_high_miles():
    route_a = make_plan(
        name="A",
        severe_mi=5,
        high_mi=0,
    )
    route_b = make_plan(
        name="B",
        severe_mi=2,
        high_mi=100,
    )

    ranked = prepare_ranking([route_a, route_b])

    assert [p["name"] for p in ranked] == ["B", "A"]


def test_fewer_high_risk_miles_wins_when_severe_miles_tie():
    route_a = make_plan(name="A", severe_mi=2, high_mi=10)
    route_b = make_plan(name="B", severe_mi=2, high_mi=5)

    ranked = prepare_ranking([route_a, route_b])

    assert [p["name"] for p in ranked] == ["B", "A"]


def test_lower_average_score_wins_when_previous_fields_tie():
    route_a = make_plan(name="A", avg_score=3.5)
    route_b = make_plan(name="B", avg_score=2.5)

    ranked = prepare_ranking([route_a, route_b])

    assert [p["name"] for p in ranked] == ["B", "A"]


def test_shorter_duration_wins_when_risk_fields_tie():
    route_a = make_plan(name="A", duration_min=200)
    route_b = make_plan(name="B", duration_min=150)

    ranked = prepare_ranking([route_a, route_b])

    assert [p["name"] for p in ranked] == ["B", "A"]




def test_complete_routes_are_ranked_best_to_worst():
    route_a = make_plan(name="A", severe_mi=5)
    route_b = make_plan(name="B", high_mi=5)
    route_c = make_plan(name="C", no_travel_mi=2)

    ranked = prepare_ranking([route_c, route_a, route_b])

    assert [p["name"] for p in ranked] == ["B", "A", "C"]
    assert [p["rank"] for p in ranked] == [1, 2, 3]
    assert [p["disqualified"] for p in ranked] == [
        False,
        False,
        True,
    ]


def test_identical_keys_preserve_input_order():
    route_a = make_plan(name="A")
    route_b = make_plan(name="B")
    route_c = make_plan(name="C")

    ranked = prepare_ranking([route_b, route_a, route_c])

    assert [p["name"] for p in ranked] == ["B", "A", "C"]


def test_empty_input_returns_empty_list():
    assert prepare_ranking([]) == []




def test_prepare_ranking_does_not_modify_original_plans():
    route_a = make_plan(name="A", severe_mi=3)
    route_b = make_plan(name="B", severe_mi=1)

    original_a = route_a.copy()
    original_b = route_b.copy()

    prepare_ranking([route_a, route_b])

    assert route_a == original_a
    assert route_b == original_b
    assert "rank" not in route_a
    assert "disqualified" not in route_b


def test_ranked_results_are_copies():
    route = make_plan(name="A")

    ranked = prepare_ranking([route])

    assert ranked[0] is not route




@pytest.mark.parametrize(
    "bad_value",
    [
        -1,
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        False,
        "10",
        None,
    ],
)
def test_rank_route_rejects_invalid_numeric_values(bad_value):
    plan = make_plan()
    plan["high_mi"] = bad_value

    with pytest.raises(ValueError):
        rank_route(plan)


@pytest.mark.parametrize(
    "field",
    [
        "no_travel_mi",
        "severe_mi",
        "high_mi",
        "avg_score",
        "duration_min",
    ],
)
def test_rank_route_rejects_missing_fields(field):
    plan = make_plan()
    del plan[field]

    with pytest.raises(ValueError):
        rank_route(plan)


def test_is_disqualified_rejects_invalid_no_travel_value():
    plan = make_plan(no_travel_mi=float("nan"))

    with pytest.raises(ValueError):
        is_disqualified(plan)


def test_extremely_large_integer_raises_value_error():
    plan = make_plan(duration_min=10**10000)

    with pytest.raises(ValueError):
        rank_route(plan)


def test_disqualified_route_still_requires_all_ranking_fields():
    plan = make_plan(no_travel_mi=1)
    del plan["duration_min"]

    with pytest.raises(ValueError):
        rank_route(plan)
