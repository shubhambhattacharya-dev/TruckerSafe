"""URL configuration for the routing API."""

from django.urls import path

from apps.routing.api.views import route_plan

app_name = "routing_api"

urlpatterns = [
    path("route-plans/", route_plan, name="route-plan"),
    path("route-plans", route_plan),
]
