"""Template generator for route plan explainers."""

from __future__ import annotations

from typing import Any, Mapping


def generate_template_explainer(
    recommended_route: Mapping[str, Any],
    all_routes: list[Mapping[str, Any]],
    load_lb: int,
) -> dict[str, Any]:
    """Generate deterministic, fact-grounded headline and bullet points."""
    rec_id = recommended_route.get("id", 1)
    risk = recommended_route.get("risk", {})
    summary = recommended_route.get("summary", {})

    avg_score = float(risk.get("avg_score", 1.0))
    severe_mi = float(risk.get("severe_mi", 0.0))
    no_travel_mi = float(risk.get("no_travel_mi", 0.0))
    duration_min = float(summary.get("duration_min", 0.0))

    headline = f"Route {rec_id} is the safest choice for a {load_lb:,} lb load"

    bullets = [
        (
            f"Route {rec_id} averages {avg_score:.2f} risk score with "
            f"{severe_mi:.0f} Severe miles and {no_travel_mi:.0f} No-Travel miles."
        )
    ]

    disqualified_route = next(
        (r for r in all_routes if r.get("disqualified")), None
    )
    if disqualified_route:
        dq_id = disqualified_route.get("id", "?")
        reason = disqualified_route.get("reason") or "adverse weather exceeds safe limits for this load"
        bullets.append(f"Route {dq_id} is disqualified: {reason}.")
    else:
        bullets.append(
            "All candidate routes remain qualified; ranking decided on Severe and High risk miles."
        )

    duration_hours = duration_min / 60.0
    bullets.append(
        f"Estimated travel time is {duration_hours:.1f} hours ({int(duration_min)} minutes) on the road."
    )

    return {
        "headline": headline,
        "bullets": bullets,
    }
