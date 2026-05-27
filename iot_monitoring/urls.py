from django.contrib import admin
from django.urls import include, path

from accounts.views import DashboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("api/accounts/", include("accounts.urls")),
    path("api/devices/", include("devices.urls")),
    path("api/telemetry/", include("telemetry.urls")),
    path("api/alerts/", include("alerts.urls")),
    path("api/ai/", include("ai_agent.urls")),
]
