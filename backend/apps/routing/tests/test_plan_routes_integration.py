
"""Integration tests for TruckerSafe route-planning orchestration."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.routing.api.views import plan_routes
from apps.routing.services.risk.engine import RiskBand
from apps.routing.services.weather.base import HourlyWeather


class PlanRoutesIntegrationTests(SimpleTestCase):
    """Exercise real internal services with mocked external providers."""

    def setUp(self):
        self.departure = datetime(
            2026, 10, 15, 12, 0, tzinfo=timezone.utc
        )

        # GeoJSON coordinates use [longitude, latitude].
        self.route = {
            "geometry": [
                [-87.6300, 41.8800],
                [-87.6300, 42.8800],
            ],
            "distance_meters": 111_000.0,
            "duration_seconds": 7_200.0,
        }

        self.origin_coordinates = (41.88, -87.63)
        self.destination_coordinates = (42.88, -87.63)

    def make_weather(self):
        """Create deterministic, complete weather for any requested hour."""
        client = MagicMock()

        def get_hourly_forecast(latitude, longitude, start, end):
            return [
                HourlyWeather(
                    timestamp=start,
                    wind_mph=10.0,
                    precipitation_inches=0.0,
                    snowfall_inches=0.0,
                )
            ]

        client.get_hourly_forecast.side_effect = get_hourly_forecast
        return client

    @patch("apps.routing.api.views.Geocoder")
    @patch("apps.routing.api.views.OSRMAdapter")
    @patch("apps.routing.api.views.OpenMeteoAdapter")
    @patch.dict(
        "os.environ",
        {"GEOCODER_USER_AGENT": "TruckerSafe tests contact:test@example.com"},
    )
    def test_complete_route_plan_uses_real_internal_services(
        self,
        mock_weather_class,
        mock_router_class,
        mock_geocoder_class,
    ):
        geocoder = mock_geocoder_class.return_value
        geocoder.geocode.side_effect = [
            self.origin_coordinates,
            self.destination_coordinates,
        ]

        router = mock_router_class.return_value
        router.get_routes.return_value = [self.route]

        weather = self.make_weather()
        mock_weather_class.return_value = weather

        result = plan_routes(
            origin="Chicago, IL",
            destination="Denver, CO",
            departure_time=self.departure,
            load_lb=20_000,
            checkpoint_interval_miles=25,
        )

        self.assertEqual(result["routes_found"], 1)
        self.assertEqual(len(result["routes"]), 1)

        route = result["routes"][0]
        self.assertEqual(route["route_id"], "route-1")
        self.assertEqual(route["rank"], 1)

        self.assertGreater(route["distance_miles"], 0)
        self.assertGreater(route["duration_seconds"], 0)

        checkpoints = route["checkpoints"]
        self.assertGreaterEqual(len(checkpoints), 2)
        self.assertAlmostEqual(checkpoints[0]["distance_miles"], 0.0)
        self.assertAlmostEqual(
            checkpoints[-1]["distance_miles"],
            route["distance_miles"],
            delta=0.001,
        )

        for checkpoint in checkpoints:
            self.assertIn("final_band", checkpoint)
            self.assertIn("incomplete_data", checkpoint)
            self.assertIsNotNone(checkpoint["weather"])
            self.assertFalse(checkpoint["incomplete_data"])
            self.assertEqual(
                checkpoint["final_band"],
                RiskBand.LOW.name,
            )

        summary = route["risk_summary"]
        self.assertIn("low_mi", summary)
        self.assertIn("no_travel_mi", summary)
        self.assertAlmostEqual(
            summary["route_distance_mi"],
            route["distance_miles"],
            delta=0.001,
        )

        # Guidebook §5 contract fields
        self.assertEqual(result["recommended_route_id"], 1)
        self.assertFalse(result["demo_data"])
        self.assertIn("explainer", result)
        self.assertIn("headline", result["explainer"])
        self.assertEqual(len(result["explainer"]["bullets"]), 3)
        self.assertIn("heatmap", result)
        self.assertEqual(len(result["heatmap"]["bbox"]), 4)
        self.assertIn("wind", result["heatmap"])
        self.assertIn("rain", result["heatmap"])
        self.assertIn("snow", result["heatmap"])

        self.assertIn("summary", route)
        self.assertIn("distance_mi", route["summary"])
        self.assertIn("duration_min", route["summary"])
        self.assertIn("eta", route["summary"])
        self.assertIn("risk", route)
        self.assertIn("polyline_simplified", route)
        self.assertGreater(len(route["polyline_simplified"]), 0)

        geocoder.geocode.assert_any_call("Chicago, IL")
        geocoder.geocode.assert_any_call("Denver, CO")
        router.get_routes.assert_called_once()

        self.assertGreaterEqual(weather.get_hourly_forecast.call_count, 2)

    @patch("apps.routing.api.views.Geocoder")
    @patch("apps.routing.api.views.OSRMAdapter")
    @patch("apps.routing.api.views.OpenMeteoAdapter")
    @patch.dict(
        "os.environ",
        {"GEOCODER_USER_AGENT": "TruckerSafe tests contact:test@example.com"},
    )
    def test_no_routes_raises_no_routes_found(
        self,
        mock_weather_class,
        mock_router_class,
        mock_geocoder_class,
    ):
        from apps.routing.api.views import NoRoutesFound

        geocoder = mock_geocoder_class.return_value
        geocoder.geocode.side_effect = [
            self.origin_coordinates,
            self.destination_coordinates,
        ]

        mock_router_class.return_value.get_routes.return_value = []

        with self.assertRaises(NoRoutesFound):
            plan_routes(
                origin="Chicago, IL",
                destination="Denver, CO",
                departure_time=self.departure,
                load_lb=20_000,
                checkpoint_interval_miles=25,
            )

        mock_weather_class.return_value.get_hourly_forecast.assert_not_called()

    @patch("apps.routing.api.views.Geocoder")
    @patch("apps.routing.api.views.OSRMAdapter")
    @patch("apps.routing.api.views.OpenMeteoAdapter")
    @patch.dict(
        "os.environ",
        {"GEOCODER_USER_AGENT": "TruckerSafe tests contact:test@example.com"},
    )
    def test_provider_clients_are_closed_after_success(
        self,
        mock_weather_class,
        mock_router_class,
        mock_geocoder_class,
    ):
        geocoder = mock_geocoder_class.return_value
        geocoder.geocode.side_effect = [
            self.origin_coordinates,
            self.destination_coordinates,
        ]

        mock_router_class.return_value.get_routes.return_value = [self.route]
        mock_weather_class.return_value = self.make_weather()

        plan_routes(
            origin="Chicago, IL",
            destination="Denver, CO",
            departure_time=self.departure,
            load_lb=20_000,
            checkpoint_interval_miles=25,
        )

        geocoder.close.assert_called_once()
        mock_router_class.return_value.close.assert_called_once()
        mock_weather_class.return_value.close.assert_called_once()