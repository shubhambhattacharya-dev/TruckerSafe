"""Models for the routing app.

Provides persistence for planned trips under the 'My Trips' feature.
"""

from django.db import models


class Trip(models.Model):
    """Persist planned truck trips for retrieval in 'My Trips'."""

    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    load_lb = models.PositiveIntegerField()
    checkpoint_interval_miles = models.PositiveSmallIntegerField(default=25)
    created_at = models.DateTimeField(auto_now_add=True)
    response_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Trip"
        verbose_name_plural = "Trips"

    def __str__(self) -> str:
        return f"{self.origin} → {self.destination} ({self.load_lb} lb)"
