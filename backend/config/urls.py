
"""Root URL configuration for TruckerSafe."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path

from apps.routing.api.views import route_plan


def healthz(request):
    """Return a basic liveness response."""
    if request.method == "HEAD":
        return HttpResponse(status=200)
    return JsonResponse({"status": "ok"})


def api_root(_request):
    """Return friendly JSON info for the root URL."""
    return JsonResponse(
        {
            "service": "TruckerSafe API",
            "status": "healthy",
            "version": "1.0.0",
            "health_check": "/healthz/",
            "endpoints": {
                "route_plans": "/api/route-plans",
                "api_v1": "/api/v1/",
            },
        }
    )


urlpatterns = [
    path("", api_root, name="api-root"),
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
