
"""Tests for the TruckerSafe route-planning API view."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from apps.routing.api.views import (
    NoRoutesFound,
    _evaluate_checkpoint,
    route_plan,
)
from apps.routing.services.risk.engine import RiskBand
from apps.routing.services.routing.base import RoutingProviderError
from apps.routing.services.weather.base import WeatherProviderError


class RoutePlanViewTests(SimpleTestCase):
    """Test request validation and route-planning error handling."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = "/api/v1/route-plans/"
        self.departure = (
            datetime.now(timezone.utc) + timedelta(hours=2)
        ).isoformat()

    def valid_payload(self):
        return {
            "origin": "Chicago, IL",
            "destination": "Denver, CO",
            "departure_time": self.departure,
            "load_lb": 20000,
            "checkpoint_interval_miles": 25,
        }

    def post(self, payload):
        request = self.factory.post(
            self.url,
            payload,
            format="json",
        )
        return route_plan(request)

    def test_invalid_request_returns_400(self):
        response = self.post({"origin": ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "invalid_request")

    @patch("apps.routing.api.views.plan_routes")
    def test_no_routes_returns_422(self, mock_plan_routes):
        mock_plan_routes.side_effect = NoRoutesFound()

        response = self.post(self.valid_payload())

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"], "no_routes_found")

    @patch("apps.routing.api.views.plan_routes")
    def test_routing_provider_failure_returns_503(self, mock_plan_routes):
        mock_plan_routes.side_effect = RoutingProviderError(
            "Provider unavailable"
        )

        response = self.post(self.valid_payload())

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["error"], "provider_unavailable")

    @patch("apps.routing.api.views.plan_routes")
    def test_weather_provider_failure_returns_503(self, mock_plan_routes):
        mock_plan_routes.side_effect = WeatherProviderError(
            "Weather unavailable"
        )

        response = self.post(self.valid_payload())

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["error"], "provider_unavailable")

    @patch("apps.routing.api.views.plan_routes")
    def test_success_returns_ranked_routes(self, mock_plan_routes):
        expected = {
            "origin": "Chicago, IL",
            "destination": "Denver, CO",
            "departure_time": self.departure,
            "load_lb": 20000,
            "checkpoint_interval_miles": 25,
            "routes_found": 1,
            "recommended_route_id": 1,
            "demo_data": False,
            "routes": [
                {
                    "id": 1,
                    "summary": {"distance_mi": 100.0, "duration_min": 90.0, "eta": self.departure},
                    "risk": {
                        "severe_mi": 0.0, "high_mi": 0.0, "moderate_mi": 0.0,
                        "low_mi": 100.0, "no_travel_mi": 0.0, "avg_score": 1.0,
                    },
                    "disqualified": False,
                    "reason": None,
                    "polyline_simplified": [[41.85, -87.65], [39.74, -104.99]],
                    "checkpoints": [],
                }
            ],
            "explainer": {"headline": "h", "bullets": []},
            "heatmap": {"bbox": [0, 0, 1, 1], "rows": 1, "cols": 1, "wind": [0], "rain": [0], "snow": [0]},
        }
        mock_plan_routes.return_value = expected

        response = self.post(self.valid_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["routes_found"], 1)
        self.assertEqual(response.data["recommended_route_id"], 1)
        self.assertEqual(response.data["routes"][0]["id"], 1)
        self.assertEqual(
            response.data["routes"][0]["summary"]["distance_mi"], 100.0
        )

    @patch("apps.routing.api.views.plan_routes")
    def test_internal_planning_fields_are_not_exposed(self, mock_plan_routes):
        """Internal keys must never leak into the public contract."""
        internal = {
            "routes_found": 1,
            "routes": [
                {
                    "route_id": "route-1",
                    "rank": 1,
                    "distance_miles": 100.0,
                    "duration_hours": 1.5,
                    "geometry_points": [[41.0, -87.0]],
                    "risk_summary": {"low_mi": 100.0},
                    "id": 1,
                    "summary": {},
                    "risk": {},
                    "disqualified": False,
                    "reason": None,
                    "polyline_simplified": [],
                    "checkpoints": [
                        {
                            "idx": 1,
                            "lat": 41.0,
                            "lon": -87.0,
                            "distance_mi": 0.0,
                            "eta": self.departure,
                            "location_name": "Checkpoint 1",
                            "wind_mph": 5.0,
                            "rain_in_hr": 0.0,
                            "snow_in_hr": 0.0,
                            "risk_band": "LOW",
                            "incomplete_data": False,
                            "final_band": "LOW",
                            "risk_metadata": {"reason": "x"},
                            "distance_miles": 0.0,
                            "arrival_time": self.departure,
                            "weather": {"timestamp": self.departure},
                            "missing_weather_fields": [],
                        }
                    ],
                }
            ],
        }
        mock_plan_routes.return_value = internal

        response = self.post(self.valid_payload())

        self.assertEqual(response.status_code, 200)
        route = response.data["routes"][0]
        for leaked in (
            "route_id",
            "rank",
            "distance_miles",
            "duration_hours",
            "geometry_points",
            "risk_summary",
        ):
            self.assertNotIn(leaked, route)
        checkpoint = route["checkpoints"][0]
        for leaked in ("final_band", "risk_metadata", "weather", "arrival_time"):
            self.assertNotIn(leaked, checkpoint)
        self.assertIn("risk_band", checkpoint)
        self.assertIn("incomplete_data", checkpoint)

    @patch("apps.routing.api.views.plan_routes")
    def test_provider_is_not_called_for_invalid_request(
        self,
        mock_plan_routes,
    ):
        response = self.post(
            {
                **self.valid_payload(),
                "load_lb": -1,
            }
        )

        self.assertEqual(response.status_code, 400)
        mock_plan_routes.assert_not_called()


class CheckpointWeatherTests(SimpleTestCase):
    """Test conservative handling of incomplete weather measurements."""

    def test_missing_weather_is_marked_no_travel(self):
        class FakeWeatherClient:
            def get_hourly_forecast(self, *args, **kwargs):
                return []

        arrival = datetime.now(timezone.utc) + timedelta(hours=2)

        result = _evaluate_checkpoint(
            FakeWeatherClient(),
            latitude=41.88,
            longitude=-87.63,
            distance_miles=0.0,
            arrival_time=arrival,
            load_lb=20000,
        )

        self.assertEqual(result["final_band"], RiskBand.NO_TRAVEL)
        self.assertTrue(result["incomplete_data"])
        self.assertIsNone(result["weather"])
        self.assertCountEqual(
            result["missing_weather_fields"],
            [
                "wind_mph",
                "precipitation_inches",
                "snowfall_inches",
            ],
        )

    def test_missing_measurement_is_not_treated_as_zero(self):
        from apps.routing.services.weather.base import HourlyWeather

        class FakeWeatherClient:
            def get_hourly_forecast(self, *args, **kwargs):
                bucket = args[2]
                return [
                    HourlyWeather(
                        timestamp=bucket,
                        wind_mph=10.0,
                        precipitation_inches=None,
                        snowfall_inches=0.0,
                    )
                ]

        arrival = datetime.now(timezone.utc) + timedelta(hours=2)

        result = _evaluate_checkpoint(
            FakeWeatherClient(),
            latitude=41.88,
            longitude=-87.63,
            distance_miles=0.0,
            arrival_time=arrival,
            load_lb=20000,
        )

        self.assertEqual(result["final_band"], RiskBand.NO_TRAVEL)
        self.assertTrue(result["incomplete_data"])
        self.assertIn(
            "precipitation_inches",
            result["missing_weather_fields"],
        )
