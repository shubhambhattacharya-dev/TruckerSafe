
"""Root URL configuration for TruckerSafe."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from apps.routing.api.views import route_plan


def healthz(_request):
    """Return a basic liveness response."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz, name="healthz"),
    path("api/v1/", include("apps.routing.api.urls")),
    path("api/route-plans/", route_plan),
    path("api/route-plans", route_plan),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

admin.site.site_header = "TruckerSafe Administration"
admin.site.site_title = "TruckerSafe Admin"
admin.site.index_title = "Dashboard"
