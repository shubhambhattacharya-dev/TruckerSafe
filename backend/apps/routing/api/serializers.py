
"""Request serializers for the TruckerSafe routing API."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.utils import timezone
from rest_framework import serializers


# ---------------------------------------------------------------------------
# Domain limits
# ---------------------------------------------------------------------------

MIN_LOAD_LB = 1_000
MAX_LOAD_LB = 80_000

CHECKPOINT_INTERVAL_CHOICES = (10, 25, 50)

MAX_FORECAST_HOURS = 120
MAX_LOCATION_LENGTH = 120


class RoutePlanRequestSerializer(serializers.Serializer):
    """Validate and normalize a route-planning request."""

    origin = serializers.CharField(
        max_length=MAX_LOCATION_LENGTH,
        trim_whitespace=True,
        help_text="Starting point: city, address, or place name.",
    )

    destination = serializers.CharField(
        max_length=MAX_LOCATION_LENGTH,
        trim_whitespace=True,
        help_text="Ending point: city, address, or place name.",
    )

    departure_time = serializers.DateTimeField(
        help_text=(
            "Departure time in ISO 8601 format. "
            f"Must be within {MAX_FORECAST_HOURS} hours from now."
        ),
    )

    load_lb = serializers.IntegerField(
        min_value=MIN_LOAD_LB,
        max_value=MAX_LOAD_LB,
        help_text=(
            f"Cargo weight in pounds "
            f"({MIN_LOAD_LB:,}–{MAX_LOAD_LB:,})."
        ),
    )

    checkpoint_interval_miles = serializers.IntegerField(
        default=25,
        required=False,
        help_text="Distance between weather checkpoints, in miles.",
    )

    def validate_checkpoint_interval_miles(self, value: int) -> int:
        """Restrict checkpoint interval to the supported choices."""
        if value not in CHECKPOINT_INTERVAL_CHOICES:
            raise serializers.ValidationError(
                f"Must be one of {CHECKPOINT_INTERVAL_CHOICES}."
            )
        return value

    # -----------------------------------------------------------------------
    # Field-level validation
    # -----------------------------------------------------------------------

    def validate_origin(self, value: str) -> str:
        """Reject blank origin values."""
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Origin cannot be blank."
            )

        return value

    def validate_destination(self, value: str) -> str:
        """Reject blank destination values."""
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Destination cannot be blank."
            )

        return value

    def validate_departure_time(self, value):
        """Restrict departure to the supported forecast window."""
        now = timezone.now()
        latest_departure = now + timedelta(
            hours=MAX_FORECAST_HOURS
        )

        if value < now:
            raise serializers.ValidationError(
                "Departure time cannot be in the past."
            )

        if value > latest_departure:
            raise serializers.ValidationError(
                "Departure exceeds the forecast window "
                f"(maximum {MAX_FORECAST_HOURS} hours ahead)."
            )

        return value

    # -----------------------------------------------------------------------
    # Object-level validation
    # -----------------------------------------------------------------------

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate relationships between request fields."""
        origin = attrs["origin"].casefold()
        destination = attrs["destination"].casefold()

        if origin == destination:
            raise serializers.ValidationError(
                {
                    "destination": (
                        "Destination must differ from origin."
                    )
                }
            )

        return attrs
