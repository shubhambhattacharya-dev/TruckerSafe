"""Contract tests for the TruckerSafe route-planning API."""

from datetime import timedelta
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone
from rest_framework.test import APIClient


ROUTE_PLANS_URL = "/api/v1/route-plans/"


class RoutePlanAPIContractTests(SimpleTestCase):
    """Verify the public HTTP contract of the route-planning endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "origin": "Chicago, IL",
            "destination": "Denver, CO",
            "departure_time": (
                timezone.now() + timedelta(hours=2)
            ).isoformat(),
            "load_lb": 20000,
            "checkpoint_interval_miles": 25,
        }

    def test_post_endpoint_accepts_valid_request(self):
        """A valid request reaches the route-planning service."""
        expected_response = {
            "origin": "Chicago, IL",
            "destination": "Denver, CO",
            "routes_found": 0,
            "routes": [],
        }

        with patch(
            "apps.routing.api.views.plan_routes",
            return_value=expected_response,
        ) as mock_plan_routes:
            response = self.client.post(
                ROUTE_PLANS_URL,
                self.valid_payload,
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)
        mock_plan_routes.assert_called_once()

    def test_get_method_is_not_allowed(self):
        """The endpoint accepts POST, not GET."""
        response = self.client.get(ROUTE_PLANS_URL)

        self.assertEqual(response.status_code, 405)

    def test_missing_required_field_returns_400(self):
        """Origin is required."""
        payload = self.valid_payload.copy()
        payload.pop("origin")

        with patch("apps.routing.api.views.plan_routes") as mock_plan_routes:
            response = self.client.post(
                ROUTE_PLANS_URL,
                payload,
                format="json",
            )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(mock_plan_routes.called)

    def test_invalid_checkpoint_interval_returns_400(self):
        """Only supported checkpoint intervals are accepted."""
        payload = {
            **self.valid_payload,
            "checkpoint_interval_miles": 15,
        }

        with patch("apps.routing.api.views.plan_routes") as mock_plan_routes:
            response = self.client.post(
                ROUTE_PLANS_URL,
                payload,
                format="json",
            )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(mock_plan_routes.called)

    def test_load_outside_supported_range_returns_400(self):
        """Cargo weight must be within the supported range."""
        payload = {
            **self.valid_payload,
            "load_lb": 100000,
        }

        with patch("apps.routing.api.views.plan_routes") as mock_plan_routes:
            response = self.client.post(
                ROUTE_PLANS_URL,
                payload,
                format="json",
            )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(mock_plan_routes.called)

    def test_same_origin_and_destination_returns_400(self):
        """Origin and destination must differ."""
        payload = {
            **self.valid_payload,
            "destination": self.valid_payload["origin"],
        }

        with patch("apps.routing.api.views.plan_routes") as mock_plan_routes:
            response = self.client.post(
                ROUTE_PLANS_URL,
                payload,
                format="json",
            )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(mock_plan_routes.called)

    def test_malformed_json_returns_400(self):
        """Malformed JSON is rejected before planning."""
        response = self.client.generic(
            "POST",
            ROUTE_PLANS_URL,
            data='{"origin": ',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
