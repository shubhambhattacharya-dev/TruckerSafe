"""Create a deterministic, inspection-friendly demo scenario summary.

This project has no database models to seed.  The script instead writes a
small JSON manifest that documents the Chicago-to-Denver scenario used by the
frontend fixture, including the intentionally disqualified second route.
"""

from __future__ import annotations

import json
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
OUTPUT = BACKEND_DIR / "fixtures" / "demo_scenario.json"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "origin": "Chicago, IL, USA",
        "destination": "Denver, CO, USA",
        "load_lb": 40000,
        "checkpoint_interval_miles": 25,
        "expected_routes": 3,
        "disqualified_route": 2,
        "reason": "Wind at 45-54 mph with load above 30,000 lb is No Travel.",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
