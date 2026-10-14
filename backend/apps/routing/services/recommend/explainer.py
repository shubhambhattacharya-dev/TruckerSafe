"""AI and template-based explanation for TruckerSafe route recommendations."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from apps.routing.services.recommend.templates import generate_template_explainer

logger = logging.getLogger(__name__)


def explain_route_plan(
    recommended_route: Mapping[str, Any],
    all_routes: list[Mapping[str, Any]],
    load_lb: int,
) -> dict[str, Any]:
    """Explain why the recommended route was selected.

    Uses safe template-based generation (with strict validation against computed stats).
    """
    return generate_template_explainer(
        recommended_route=recommended_route,
        all_routes=all_routes,
        load_lb=load_lb,
    )
