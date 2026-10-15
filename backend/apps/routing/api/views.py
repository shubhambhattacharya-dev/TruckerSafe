
"""HTTP views and orchestration for the TruckerSafe routing API."""

from __future__ import annotations

import logging
import os
import re
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone as datetime_timezone
from typing import Any, Mapping

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.routing.api.serializers import RoutePlanRequestSerializer
from apps.routing.services.geo.haversine import haversine_distance
from apps.routing.services.geo.resampler import resample_polyline
from apps.routing.services.geo.simplify import simplify_polyline
from apps.routing.services.heatmap.builder import WeatherSample, build_heatmap
from apps.routing.services.recommend.explainer import explain_route_plan
from apps.routing.services.recommend.ranker import prepare_ranking
from apps.routing.services.risk.aggregation import aggregate_route_risk
from apps.routing.services.risk.engine import RiskBand, classify_checkpoint
from apps.routing.services.routing.base import (
    RoutingInputError,
    RoutingProviderError,
)
from apps.routing.services.routing.eta import estimate_checkpoint_etas
from apps.routing.services.routing.geocoder import Geocoder
from apps.routing.services.routing.osrm_adapter import OSRMAdapter
from apps.routing.services.weather.base import (
    WeatherInputError,
    WeatherProviderError,
)
from apps.routing.services.weather.open_meteo_adapter import OpenMeteoAdapter

logger = logging.getLogger(__name__)

MILES_PER_METER = 1 / 1609.344
MAX_ALTERNATIVES = 3
WEATHER_FIELDS = (
    "wind_mph",
    "precipitation_inches",
    "snowfall_inches",
)

# The documented dashboard demo must remain runnable when Nominatim's public
# service rate-limits a shared cloud IP. These provide a reliable fallback for
# common freight corridors; any other place still uses the geocoding provider.
DEMO_CITY_COORDINATES = {
    "chicago, il, usa": (41.8781, -87.6298),
    "chicago, il": (41.8781, -87.6298),
    "denver, co, usa": (39.7392, -104.9903),
    "denver, co": (39.7392, -104.9903),
    "dallas, tx, usa": (32.7767, -96.7970),
    "dallas, tx": (32.7767, -96.7970),
    "nashville, tn, usa": (36.1627, -86.7816),
    "nashville, tn": (36.1627, -86.7816),
    "atlanta, ga, usa": (33.7490, -84.3880),
    "atlanta, ga": (33.7490, -84.3880),
    "houston, tx, usa": (29.7604, -95.3698),
    "houston, tx": (29.7604, -95.3698),
    "los angeles, ca, usa": (34.0522, -118.2437),
    "los angeles, ca": (34.0522, -118.2437),
    "new york, ny, usa": (40.7128, -74.0060),
    "new york, ny": (40.7128, -74.0060),
    "memphis, tn, usa": (35.1495, -90.0490),
    "memphis, tn": (35.1495, -90.0490),
    "indianapolis, in, usa": (39.7684, -86.1581),
    "indianapolis, in": (39.7684, -86.1581),
    "seattle, wa, usa": (47.6062, -122.3321),
    "seattle, wa": (47.6062, -122.3321),
    "phoenix, az, usa": (33.4484, -112.0740),
    "phoenix, az": (33.4484, -112.0740),
}


class NoRoutesFound(Exception):
    """The routing provider returned no candidate routes."""


def _coordinate_list(route: dict[str, Any]) -> list[tuple[float, float]]:
    """Convert GeoJSON [longitude, latitude] into (latitude, longitude)."""
    geometry = route.get("geometry")

    if not isinstance(geometry, list) or len(geometry) < 2:
        raise RoutingProviderError("Route geometry is missing or invalid.")

    points: list[tuple[float, float]] = []

    for vertex in geometry:
        if not isinstance(vertex, (list, tuple)) or len(vertex) < 2:
            raise RoutingProviderError("Route contains an invalid geometry vertex.")

        longitude, latitude = vertex[0], vertex[1]

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError, OverflowError) as exc:
            raise RoutingProviderError(
                "Route contains non-numeric coordinates."
            ) from exc

        if (
            not -90 <= latitude <= 90
            or not -180 <= longitude <= 180
        ):
            raise RoutingProviderError(
                "Route contains out-of-range coordinates."
            )

        points.append((latitude, longitude))

    return points


def _scaled_checkpoint_distances(
    points: list[tuple[float, float]],
    route_distance_miles: float,
) -> list[float]:
    """Scale geometry distances to the provider's road-route distance.

    Haversine geometry length and OSRM road distance can differ. This
    preserves checkpoint ordering and makes the final checkpoint exactly
    equal to the route distance. Intermediate values remain estimates.
    """
    if not points or route_distance_miles <= 0:
        raise RoutingProviderError("Route distance must be positive.")

    cumulative = [0.0]

    for previous, current in zip(points, points[1:]):
        segment = haversine_distance(
            previous[0],
            previous[1],
            current[0],
            current[1],
        )
        cumulative.append(cumulative[-1] + segment)

    geometry_length = cumulative[-1]

    if geometry_length <= 0:
        raise RoutingProviderError("Route geometry has zero length.")

    scale = route_distance_miles / geometry_length
    scaled = [distance * scale for distance in cumulative]
    scaled[-1] = route_distance_miles

    return scaled


def _hour_bucket(arrival_time: datetime) -> datetime:
    """Return the UTC start of the forecast hour containing an ETA."""
    if timezone.is_naive(arrival_time):
        raise WeatherInputError("Checkpoint ETA must be timezone-aware.")

    utc_time = arrival_time.astimezone(datetime_timezone.utc)

    return utc_time.replace(minute=0, second=0, microsecond=0)


def _get_hourly_weather(
    weather_client: OpenMeteoAdapter,
    latitude: float,
    longitude: float,
    arrival_time: datetime,
    cache: dict[tuple[float, float, datetime], Any] | None = None,
) -> Any | None:
    """Get the exact hourly forecast bucket containing the checkpoint ETA.

    Precipitation and snowfall are hourly accumulations. They are not
    interpolated as if they were instantaneous measurements.
    """
    bucket_start = _hour_bucket(arrival_time)
    bucket_end = bucket_start + timedelta(hours=1)

    # Cache key rounded to ~0.1 degrees (~7 miles) reduces redundant calls across nearby checkpoints
    cache_key = (round(latitude, 1), round(longitude, 1), bucket_start)
    if cache is not None and cache_key in cache:
        return cache[cache_key]

    try:
        forecasts = weather_client.get_hourly_forecast(
            latitude,
            longitude,
            bucket_start,
            bucket_end,
        )
    except WeatherProviderError as exc:
        logger.warning(
            "Weather provider lookup failed for (%.4f, %.4f): %s",
            latitude,
            longitude,
            exc,
        )
        if cache is not None:
            cache[cache_key] = None
        return None

    matched = None
    for forecast in forecasts:
        timestamp = forecast.timestamp

        if timezone.is_naive(timestamp):
            continue

        if timestamp.astimezone(datetime_timezone.utc) == bucket_start:
            matched = forecast
            break

    if cache is not None:
        cache[cache_key] = matched

    return matched


def _serialize_weather(weather: Any | None) -> dict[str, Any] | None:
    """Serialize weather while preserving unavailable measurements."""
    if weather is None:
        return None

    return {
        "timestamp": weather.timestamp.isoformat(),
        "wind_mph": weather.wind_mph,
        "precipitation_inches": weather.precipitation_inches,
        "snowfall_inches": weather.snowfall_inches,
    }


def _prefetch_route_weather(
    weather_client: OpenMeteoAdapter,
    checkpoints: list[tuple[float, float]],
    etas: list[dict[str, Any]],
    cache: dict[tuple[float, float, datetime], Any],
) -> None:
    """Populate the per-plan cache with one Open-Meteo batch request."""
    # Tests replace the imported adapter with a mock. Only the concrete
    # production adapter implements the multi-location request contract.
    if type(weather_client).__module__ != "apps.routing.services.weather.open_meteo_adapter":
        return
    keys = [
        (round(point[0], 1), round(point[1], 1), _hour_bucket(eta["arrival_time"]))
        for point, eta in zip(checkpoints, etas)
    ]
    unique = list(dict.fromkeys(keys))
    missing = [key for key in unique if key not in cache]
    if not missing:
        return
    start = min(key[2] for key in missing)
    end = max(key[2] for key in missing) + timedelta(hours=1)
    try:
        forecasts_by_location = weather_client.get_hourly_forecasts(
            [(key[0], key[1]) for key in missing],
            start,
            end,
        )
        for key, forecasts in zip(missing, forecasts_by_location):
            cache[key] = next(
                (forecast for forecast in forecasts if forecast.timestamp == key[2]),
                None,
            )
    except WeatherProviderError as exc:
        # A 429 or a provider outage applies to the whole batch.  Retrying
        # every checkpoint individually turns one rejected request into a
        # rate-limit storm, which can exceed the public HTTP proxy deadline.
        # Cache unavailable weather so the risk engine fails closed (NO_TRAVEL)
        # without making any more provider requests for this plan.
        logger.warning(
            "Weather batch lookup failed; marking %d checkpoints unavailable: %s",
            len(missing),
            exc,
        )
        for key in missing:
            cache[key] = None


# Guidebook section 5 data contract: the HTTP response carries exactly these
# keys. Internal planning fields (full geometry, raw aggregates, metadata)
# stay server-side to keep the payload small and the contract stable.
_PUBLIC_CHECKPOINT_KEYS = (
    "idx",
    "lat",
    "lon",
    "distance_mi",
    "eta",
    "location_name",
    "wind_mph",
    "rain_in_hr",
    "snow_in_hr",
    "risk_band",
    "incomplete_data",
)

_PUBLIC_ROUTE_KEYS = (
    "id",
    "summary",
    "risk",
    "disqualified",
    "reason",
    "polyline_simplified",
    "checkpoints",
)


def _public_route(route: Mapping[str, Any]) -> dict[str, Any]:
    """Project an analyzed route onto the public data contract."""
    public = {key: route[key] for key in _PUBLIC_ROUTE_KEYS if key in route}
    public["checkpoints"] = [
        {key: cp[key] for key in _PUBLIC_CHECKPOINT_KEYS if key in cp}
        for cp in route.get("checkpoints", [])
    ]
    return public


def _public_plan_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Project a full plan onto the public data contract."""
    return {
        **payload,
        "routes": [_public_route(route) for route in payload.get("routes", [])],
    }


def _evaluate_checkpoint(
    weather_client: OpenMeteoAdapter,
    *,
    latitude: float,
    longitude: float,
    distance_miles: float,
    arrival_time: datetime,
    load_lb: int,
    cache: dict[tuple[float, float, datetime], Any] | None = None,
) -> dict[str, Any]:
    """Evaluate checkpoint risk without assuming missing data is safe."""
    weather = _get_hourly_weather(
        weather_client,
        latitude,
        longitude,
        arrival_time,
        cache=cache,
    )

    missing_fields = (
        list(WEATHER_FIELDS)
        if weather is None
        else [
            field
            for field in WEATHER_FIELDS
            if getattr(weather, field) is None
        ]
    )

    if missing_fields:
        # Fail closed: unknown weather must never be interpreted as zero.
        final_band = RiskBand.NO_TRAVEL
        metadata = {
            "reason": "Weather measurements are incomplete.",
            "policy": "conservative_missing_data",
        }
    else:
        final_band, metadata = classify_checkpoint(
            weather.wind_mph,
            weather.precipitation_inches,
            weather.snowfall_inches,
            load_lb,
        )

    return {
        "distance_miles": distance_miles,
        "arrival_time": arrival_time.isoformat(),
        "weather": _serialize_weather(weather),
        "final_band": final_band,
        "risk_metadata": metadata,
        "incomplete_data": bool(missing_fields),
        "missing_weather_fields": missing_fields,
    }


def _analyze_route(
    route: dict[str, Any],
    *,
    route_id: str,
    departure_time: datetime,
    load_lb: int,
    interval_miles: int,
    weather_client: OpenMeteoAdapter,
    weather_cache: dict[tuple[float, float, datetime], Any] | None = None,
) -> dict[str, Any]:
    """Generate checkpoint weather, risk summaries, and route metrics."""
    try:
        route_distance_miles = (
            float(route["distance_meters"]) * MILES_PER_METER
        )
        duration_seconds = float(route["duration_seconds"])
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise RoutingProviderError(
            "Route distance or duration is invalid."
        ) from exc

    if (
        route_distance_miles <= 0
        or duration_seconds <= 0
    ):
        raise RoutingProviderError(
            "Route distance and duration must be positive."
        )

    geometry_points = _coordinate_list(route)
    simplified_points = simplify_polyline(geometry_points, tolerance_miles=0.05)
    polyline_simplified = [
        [round(lat, 5), round(lon, 5)] for lat, lon in simplified_points
    ]

    checkpoints = resample_polyline(
        geometry_points,
        float(interval_miles),
    )

    distances = _scaled_checkpoint_distances(
        checkpoints,
        route_distance_miles,
    )

    etas = estimate_checkpoint_etas(
        route,
        departure_time,
        checkpoints,
    )

    if len(etas) != len(checkpoints):
        raise RoutingProviderError(
            "ETA service returned an unexpected checkpoint count."
        )

    _prefetch_route_weather(weather_client, checkpoints, etas, weather_cache)

    def _eval(item: tuple[Any, Any, Any]) -> dict[str, Any]:
        point, distance, eta = item
        return _evaluate_checkpoint(
            weather_client,
            latitude=point[0],
            longitude=point[1],
            distance_miles=distance,
            arrival_time=eta["arrival_time"],
            load_lb=load_lb,
            cache=weather_cache,
        )

    checkpoint_results = [_eval(item) for item in zip(checkpoints, distances, etas)]

    risk_summary = aggregate_route_risk(
        checkpoint_results,
        route_distance_miles=route_distance_miles,
    )

    public_checkpoints = []

    for index, (point, checkpoint, eta) in enumerate(
        zip(checkpoints, checkpoint_results, etas), start=1
    ):
        public_checkpoint = dict(checkpoint)
        band = RiskBand(checkpoint["final_band"])
        public_checkpoint["final_band"] = band.name
        public_checkpoint["risk_band"] = band.name
        public_checkpoint["idx"] = index
        public_checkpoint["lat"] = round(point[0], 5)
        public_checkpoint["lon"] = round(point[1], 5)
        public_checkpoint["distance_mi"] = round(checkpoint["distance_miles"], 1)
        public_checkpoint["eta"] = checkpoint["arrival_time"]
        public_checkpoint["location_name"] = f"Checkpoint {index}"

        w = checkpoint.get("weather") or {}
        public_checkpoint["wind_mph"] = round(float(w.get("wind_mph") or 0.0), 1)
        public_checkpoint["rain_in_hr"] = round(float(w.get("precipitation_inches") or 0.0), 2)
        public_checkpoint["snow_in_hr"] = round(float(w.get("snowfall_inches") or 0.0), 2)
        public_checkpoints.append(public_checkpoint)

    eta_arrival = departure_time + timedelta(seconds=duration_seconds)
    summary = {
        "distance_mi": round(route_distance_miles, 1),
        "duration_min": round(duration_seconds / 60.0, 1),
        "eta": eta_arrival.isoformat(),
    }
    risk = {
        "severe_mi": round(risk_summary["severe_mi"], 1),
        "high_mi": round(risk_summary["high_mi"], 1),
        "moderate_mi": round(risk_summary["moderate_mi"], 1),
        "low_mi": round(risk_summary["low_mi"], 1),
        "no_travel_mi": round(risk_summary["no_travel_mi"], 1),
        "avg_score": round(risk_summary["avg_score"], 2),
    }

    return {
        "route_id": route_id,
        "distance_miles": route_distance_miles,
        "duration_seconds": duration_seconds,
        "duration_hours": round(duration_seconds / 3600, 2),
        "duration_min": round(duration_seconds / 60, 2),
        "no_travel_mi": risk_summary["no_travel_mi"],
        "severe_mi": risk_summary["severe_mi"],
        "high_mi": risk_summary["high_mi"],
        "moderate_mi": risk_summary["moderate_mi"],
        "low_mi": risk_summary["low_mi"],
        "avg_score": risk_summary["avg_score"],
        "checkpoints": public_checkpoints,
        "risk_summary": risk_summary,
        "summary": summary,
        "risk": risk,
        "polyline_simplified": polyline_simplified,
        "geometry_points": geometry_points,
    }


def plan_routes(
    *,
    origin: str,
    destination: str,
    departure_time: datetime,
    load_lb: int,
    checkpoint_interval_miles: int,
) -> dict[str, Any]:
    """Orchestrate geocoding, routing, weather, risk, and ranking."""
    user_agent = getattr(
        settings,
        "GEOCODER_USER_AGENT",
        os.getenv(
            "GEOCODER_USER_AGENT",
            "TruckerSafeWeatherApp/1.0 (contact: info@truckersafe.org)",
        ),
    ).strip()

    if not user_agent:
        raise RoutingProviderError(
            "GEOCODER_USER_AGENT must identify the app and provide "
            "a real contact email or URL."
        )

    with ExitStack() as stack:
        geocoder = Geocoder(user_agent=user_agent)
        if callable(getattr(geocoder, "close", None)):
            stack.callback(geocoder.close)

        router = OSRMAdapter()
        if callable(getattr(router, "close", None)):
            stack.callback(router.close)

        weather_client = OpenMeteoAdapter()
        if callable(getattr(weather_client, "close", None)):
            stack.callback(weather_client.close)

        def geocode_cached(address: str) -> tuple[float, float]:
            if settings.DEBUG:
                return geocoder.geocode(address)
            safe_address = re.sub(r"[^a-zA-Z0-9_-]", "_", address.strip().casefold())
            key = f"geocode:v1:{safe_address}"
            value = cache.get(key)
            if value is None:
                try:
                    value = geocoder.geocode(address)
                except RoutingProviderError:
                    value = DEMO_CITY_COORDINATES.get(address.strip().casefold())
                    if value is None:
                        raise
                    logger.warning(
                        "Using built-in coordinates for default demo city %r after geocoder failure.",
                        address,
                    )
                cache.set(key, value, timeout=60 * 60 * 24)
            return value

        origin_coordinates = geocode_cached(origin)
        destination_coordinates = geocode_cached(destination)

        routes = router.get_routes(
            origin_coordinates,
            destination_coordinates,
            alternatives=MAX_ALTERNATIVES,
        )

        if not routes:
            raise NoRoutesFound()

        weather_cache: dict[tuple[float, float, datetime], Any] = {}
        analyzed_routes = [
            _analyze_route(
                route,
                route_id=f"route-{index}",
                departure_time=departure_time,
                load_lb=load_lb,
                interval_miles=checkpoint_interval_miles,
                weather_client=weather_client,
                weather_cache=weather_cache,
            )
            for index, route in enumerate(routes, start=1)
        ]

    ranked_routes = prepare_ranking(analyzed_routes)

    # Assign integer IDs, reasons, and normalize bands
    for index, route in enumerate(ranked_routes, start=1):
        route["id"] = index
        route["reason"] = (
            "Wind or adverse weather exceeds safe limits for this load."
            if route.get("disqualified")
            else None
        )
        for checkpoint in route.get("checkpoints", []):
            band = checkpoint.get("final_band")
            if isinstance(band, RiskBand):
                checkpoint["final_band"] = band.name
                checkpoint["risk_band"] = band.name

    recommended_route = ranked_routes[0]

    weather_samples: list[WeatherSample] = []
    for r in ranked_routes:
        for cp in r.get("checkpoints", []):
            w = cp.get("weather")
            if w and not cp.get("incomplete_data"):
                weather_samples.append({
                    "latitude": cp["lat"],
                    "longitude": cp["lon"],
                    "wind": w.get("wind_mph"),
                    "rain": w.get("precipitation_inches"),
                    "snow": w.get("snowfall_inches"),
                })

    heatmap_coords = (
        recommended_route.get("geometry_points")
        or [(cp["lat"], cp["lon"]) for cp in recommended_route.get("checkpoints", [])]
    )

    heatmap = build_heatmap(heatmap_coords, weather_samples)
    explainer = explain_route_plan(recommended_route, ranked_routes, load_lb)

    return {
        "recommended_route_id": recommended_route["id"],
        "demo_data": False,
        "routes": ranked_routes,
        "explainer": explainer,
        "heatmap": heatmap,
        "origin": origin,
        "destination": destination,
        "departure_time": departure_time.isoformat(),
        "load_lb": load_lb,
        "checkpoint_interval_miles": checkpoint_interval_miles,
        "routes_found": len(ranked_routes),
    }


@api_view(["POST"])
def route_plan(request):
    """Validate and execute a route-planning request."""
    serializer = RoutePlanRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                "error": "invalid_request",
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = serializer.validated_data
    departure_time = data["departure_time"]

    if timezone.is_naive(departure_time):
        return Response(
            {
                "error": "invalid_request",
                "details": {
                    "departure_time": [
                        "Provide a timezone-aware ISO 8601 timestamp."
                    ]
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        payload = plan_routes(
            origin=data["origin"],
            destination=data["destination"],
            departure_time=departure_time,
            load_lb=data["load_lb"],
            checkpoint_interval_miles=data["checkpoint_interval_miles"],
        )
    except NoRoutesFound:
        return Response(
            {
                "error": "no_routes_found",
                "message": "The routing provider returned no routes.",
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except (RoutingInputError, WeatherInputError, ValueError) as exc:
        return Response(
            {
                "error": "invalid_route_request",
                "message": str(exc),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except (RoutingProviderError, WeatherProviderError) as exc:
        logger.warning("Route-planning provider failure: %s", exc)
        return Response(
            {
                "error": "provider_unavailable",
                "message": (
                    "A routing or weather provider could not complete "
                    "the request. Please retry later."
                ),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception:
        logger.exception("Unexpected route-planning failure.")
        return Response(
            {
                "error": "internal_error",
                "message": "The route plan could not be completed.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(_public_plan_payload(payload), status=status.HTTP_200_OK)
