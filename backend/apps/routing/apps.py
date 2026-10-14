"""Django application configuration for routing."""

from django.apps import AppConfig


class RoutingConfig(AppConfig):
    """Configuration for the routing app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.routing"
    verbose_name = "Routing"
