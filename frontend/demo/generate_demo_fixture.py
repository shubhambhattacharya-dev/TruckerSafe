"""
Generate the TruckerSafe demo fixture by running the REAL backend services.

Reads backend code (no modifications), calls live OSRM, then runs the actual
pipeline: OSRMAdapter -> resample_polyline -> classify_checkpoint ->
aggregate_route_risk -> prepare_ranking. Writes frontend/src/api/demoFixture.json
matching the /api/route-plans data contract (guidebook section 5).

Run from repo root:
    backend/venv/Scripts/python.exe frontend/demo/generate_demo_fixture.py
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))

from apps.routing.services.routing.osrm_adapter import OSRMAdapter  # noqa: E402
from apps.routing.services.geo.haversine import haversine_distance  # noqa: E402
from apps.routing.services.geo.resampler import resample_polyline  # noqa: E402
from apps.routing.services.geo.simplify import simplify_polyline  # noqa: E402
from apps.routing.services.risk.engine import classify_checkpoint  # noqa: E402
from apps.routing.services.risk.aggregation import aggregate_route_risk  # noqa: E402
from apps.routing.services.recommend.ranker import prepare_ranking  # noqa: E402

CHICAGO = (41.8781, -87.6298)
DENVER = (39.7392, -104.9903)
KANSAS_CITY = (39.0997, -94.5786)  # via-point if OSRM returns only 2 alternates
LOAD_LB = 40_000
INTERVAL_MI = 25
DEPARTURE = dt.datetime(2026, 10, 15, 8, 0, tzinfo=dt.timezone(dt.timedelta(hours=-5)))

# Nearest-city labels for checkpoint names (no geocoder service exists yet).
CITIES: list[tuple[str, float, float]] = [
    ("Chicago, IL", 41.878, -87.630), ("Joliet, IL", 41.525, -88.081),
    ("DeKalb, IL", 41.929, -88.750), ("Davenport, IA", 41.523, -90.577),
    ("Iowa City, IA", 41.661, -91.530), ("Ames, IA", 42.030, -93.620),
    ("Des Moines, IA", 41.586, -93.625), ("Omaha, NE", 41.257, -95.995),
    ("Lincoln, NE", 40.808, -96.700), ("Kearney, NE", 40.700, -99.083),
    ("North Platte, NE", 41.123, -100.765), ("Ogallala, NE", 41.128, -101.719),
    ("Julesburg, CO", 40.988, -102.264), ("Sterling, CO", 40.626, -103.208),
    ("Fort Morgan, CO", 40.250, -103.800), ("Limón, CO", 39.264, -103.692),
    ("Aurora, CO", 39.740, -104.830), ("Denver, CO", 39.739, -104.990),
    ("Kansas City, MO", 39.100, -94.579), ("Topeka, KS", 39.048, -95.678),
    ("Salina, KS", 38.840, -97.611), ("Hays, KS", 38.879, -99.327),
    ("Colby, KS", 39.396, -101.052), ("St. Joseph, MO", 39.769, -94.847),
    ("Sioux Falls, SD", 43.550, -96.730), ("Sioux City, IA", 42.499, -96.400),
    ("Cheyenne, WY", 41.140, -104.820), ("Casper, WY", 42.867, -106.313),
    ("Burlington, IA", 40.808, -91.113), ("Omaha suburbs, NE", 41.150, -96.040),
]


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return haversine_distance(a[0], a[1], b[0], b[1])


def nearest_city(lat: float, lon: float, fallback_mi: float) -> str:
    best, best_d = None, 1e9
    for name, cla, clo in CITIES:
        d = _dist((lat, lon), (cla, clo))
        if d < best_d:
            best, best_d = name, d
    return best if best_d <= 30.0 else f"Mile {fallback_mi:.0f} · corridor"


def bump(f: float, center: float, width: float, peak: float) -> float:
    return peak * math.exp(-((f - center) / width) ** 2)


def weather_at(persona: str, f: float) -> tuple[float, float, float]:
    """Synthetic but rule-realistic forecast along a route (fraction f in 0..1)."""
    if persona == "clean":        # peak wind 44 (High band; load not > 40k) + one Severe rain cell
        wind = 9.0 + bump(f, 0.42, 0.20, 35.0)
        rain = bump(f, 0.63, 0.055, 0.55)
        snow = 0.005 * bump(f, 0.80, 0.10, 1.0)
    elif persona == "wind":       # peak 58 mph -> No Travel for ANY load
        wind = 11.0 + bump(f, 0.55, 0.26, 47.0)
        rain = 0.18 * bump(f, 0.35, 0.10, 1.0)
        snow = 0.0
    else:                         # "snow": heavy mountain snow (Severe), modest wind
        wind = 8.0 + bump(f, 0.50, 0.35, 18.0)
        rain = 0.12 * bump(f, 0.40, 0.12, 1.0)
        snow = bump(f, 0.70, 0.17, 2.5)
    return round(wind, 1), round(rain, 2), round(snow, 2)


def fetch_routes() -> list[dict]:
    with OSRMAdapter() as osrm:
        routes = []
        for r in osrm.get_routes(CHICAGO, DENVER, alternatives=3):
            # Adapter preserves GeoJSON [lon, lat]; pipeline expects (lat, lon).
            routes.append({
                "geometry": [(v[1], v[0]) for v in r["geometry"]],
                "distance_meters": r["distance_meters"],
                "duration_seconds": r["duration_seconds"],
            })
        if len(routes) < 3:  # stitch a real via-point route; never fabricate geometry
            legs = []
            dm = ds = 0.0
            for a, b in ((CHICAGO, KANSAS_CITY), (KANSAS_CITY, DENVER)):
                # OSRM's alternatives param counts EXTRA routes, so alternatives=1
                # can return 2; request 2 and keep the primary route.
                leg = osrm.get_routes(a, b, alternatives=2)[0]
                legs.append([(v[1], v[0]) for v in leg["geometry"]])
                dm += leg["distance_meters"]
                ds += leg["duration_seconds"]
            geo = legs[0] + legs[1][1:]
            routes.append({"geometry": geo, "distance_meters": dm, "duration_seconds": ds})
    return routes[:3]


def cumulative_distances(geometry: list[tuple[float, float]]) -> list[float]:
    out, total = [0.0], 0.0
    for i in range(1, len(geometry)):
        total += _dist(geometry[i - 1], geometry[i])
        out.append(total)
    return out


def build_route(rid: int, raw: dict, persona: str) -> dict:
    geometry = raw["geometry"]
    cum = cumulative_distances(geometry)
    total_mi = cum[-1]
    duration_min = round(raw["duration_seconds"] / 60.0, 1)

    points = resample_polyline(geometry, INTERVAL_MI)
    n = len(points)
    checkpoints, max_wind, wind_f = [], 0.0, 0.0
    for i, (lat, lon) in enumerate(points):
        dist = total_mi if i == n - 1 else i * INTERVAL_MI
        f = dist / total_mi
        wind, rain, snow = weather_at(persona, f)
        if wind > max_wind:
            max_wind, wind_f = wind, f
        band, _meta = classify_checkpoint(wind, rain, snow, LOAD_LB)
        eta = DEPARTURE + dt.timedelta(minutes=duration_min * f)
        checkpoints.append({
            "idx": i + 1,
            "lat": round(lat, 5), "lon": round(lon, 5),
            "distance_mi": round(dist, 1),
            "distance_miles": round(dist, 1),  # aggregation's key name
            "eta": eta.isoformat(),
            "location_name": nearest_city(lat, lon, dist),
            "wind_mph": wind, "rain_in_hr": rain, "snow_in_hr": snow,
            "risk_band": band.name,
        })

    agg = aggregate_route_risk(checkpoints)
    mid = points[n // 2]
    plan = {
        "id": rid,
        "summary": {
            "distance_mi": round(total_mi, 0),
            "duration_min": duration_min,
            "eta": (DEPARTURE + dt.timedelta(minutes=duration_min)).isoformat(),
        },
        "risk": {k: round(agg[k], 1) for k in
                 ("severe_mi", "high_mi", "moderate_mi", "low_mi", "no_travel_mi", "avg_score")},
        "disqualified": agg["no_travel_mi"] > 0,
        "reason": None,
        "route_name": f"via {nearest_city(mid[0], mid[1], total_mi / 2).split(',')[0]}",
        "polyline_simplified": [[round(p[0], 5), round(p[1], 5)]
                                for p in simplify_polyline(geometry, 0.06)],
        "checkpoints": checkpoints,
        "_max_wind": max_wind,
        "_wind_f": wind_f,
    }
    if plan["disqualified"]:
        rule = ("Sustained wind ≥ 55 mph → No Travel for ANY load"
                if max_wind >= 55 else
                f"Wind 45–54 mph with a {LOAD_LB:,} lb load (> 30,000 lb) → No Travel")
        plan["reason"] = f"{rule}. Peak forecast wind {max_wind:.0f} mph en route."
    return plan


def build_heatmap(routes: list[dict]) -> dict:
    lats = [p[0] for r in routes for p in r["polyline_simplified"]]
    lons = [p[1] for r in routes for p in r["polyline_simplified"]]
    w, s, e, n = min(lons) - 1.2, min(lats) - 1.2, max(lons) + 1.2, max(lats) + 1.2
    cols, rows = 90, 50
    storms = []  # (center lat, lon, sigma_deg, wind, rain, snow)
    for r in routes:
        pts = r["polyline_simplified"]
        c = pts[min(int(r["_wind_f"] * len(pts)), len(pts) - 1)]
        persona = {1: "clean", 2: "wind", 3: "snow"}[r["id"]]
        if persona == "wind":
            storms.append((c[0], c[1], 1.45, 52.0, 0.15, 0.0))
        elif persona == "clean":
            rc = pts[int(0.63 * len(pts))]
            storms.append((c[0], c[1], 1.10, 26.0, 0.0, 0.0))
            storms.append((rc[0], rc[1], 0.75, 8.0, 0.62, 0.0))
        else:
            sc = pts[int(0.70 * len(pts))]
            storms.append((sc[0], sc[1], 1.05, 12.0, 0.0, 2.55))
            storms.append((c[0], c[1], 1.30, 18.0, 0.0, 0.0))
    wind, rain, snow = [], [], []
    for row in range(rows):
        lat = n - (row + 0.5) * (n - s) / rows
        for col in range(cols):
            lon = w + (col + 0.5) * (e - w) / cols
            cw = 7.0 + 4.0 * (lon - w) / (e - w)  # westerly base gradient
            cr, cs = 0.01, 0.0
            for sla, slo, sig, sw, sr, ss in storms:
                d2 = ((lat - sla) * 111.0) ** 2 + ((lon - slo) * 111.0 * math.cos(math.radians(lat))) ** 2
                k = math.exp(-d2 / (2 * (sig * 111.0) ** 2))
                cw += sw * k
                cr += sr * k
                cs += ss * k
            wind.append(round(cw, 1))
            rain.append(round(cr, 2))
            snow.append(round(cs, 2))
    return {"bbox": [round(w, 3), round(s, 3), round(e, 3), round(n, 3)],
            "rows": rows, "cols": cols, "wind": wind, "rain": rain, "snow": snow}


def main() -> None:
    raw = fetch_routes()
    personas = ["clean", "wind", "snow"]
    routes = [build_route(i + 1, raw[i], personas[i]) for i in range(3)]

    ranked = prepare_ranking([{
        "id": r["id"],
        "no_travel_mi": r["risk"]["no_travel_mi"],
        "severe_mi": r["risk"]["severe_mi"],
        "high_mi": r["risk"]["high_mi"],
        "avg_score": r["risk"]["avg_score"],
        "duration_min": r["summary"]["duration_min"],
    } for r in routes])
    order = {p["id"]: p["rank"] for p in ranked}
    routes.sort(key=lambda r: order[r["id"]])
    for i, r in enumerate(routes):
        r["id"] = i + 1
    rec = routes[0]
    dq = next((r for r in routes if r["disqualified"]), None)

    explainer = {
        "headline": f"Route {rec['id']} is the safest choice for a {LOAD_LB:,} lb load",
        "bullets": [
            f"Route {rec['id']} averages {rec['risk']['avg_score']:.2f} risk score with "
            f"{rec['risk']['severe_mi']:.0f} Severe miles and zero No-Travel miles.",
            (f"Route {dq['id']} is disqualified: peak wind {dq['_max_wind']:.0f} mph exceeds "
             f"safe limits for this load." if dq else
             "All routes remain qualified; ranking decided on Severe miles."),
            f"Arrival {dt.datetime.fromisoformat(rec['summary']['eta']):%I:%M %p} after "
            f"{rec['summary']['duration_min'] / 60:.1f} h on the road.",
        ],
    }

    fixture = {
        "request": {
            "origin": "Chicago, IL", "destination": "Denver, CO",
            "departure_time": DEPARTURE.isoformat(),
            "load_lb": LOAD_LB, "checkpoint_interval_miles": INTERVAL_MI,
        },
        "recommended_route_id": rec["id"],
        "demo_data": True,
        "routes": [{k: v for k, v in r.items() if not k.startswith("_")} for r in routes],
        "explainer": explainer,
        "heatmap": build_heatmap(routes),
    }

    out = REPO / "frontend" / "src" / "api" / "demoFixture.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fixture, indent=1), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB)")
    for r in routes:
        print(f"  route {r['id']} ({r['route_name']}): {r['summary']['distance_mi']:.0f} mi, "
              f"risk={r['risk']}, dq={r['disqualified']}")


if __name__ == "__main__":
    main()
