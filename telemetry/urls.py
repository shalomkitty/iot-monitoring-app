from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import TelemetryIngestView, TelemetryPointViewSet

router = DefaultRouter()
router.register("points", TelemetryPointViewSet, basename="telemetry-point")

urlpatterns = [
    path("ingest/", TelemetryIngestView.as_view(), name="telemetry-ingest"),
]
urlpatterns += router.urls
