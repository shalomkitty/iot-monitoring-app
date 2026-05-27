from rest_framework.routers import DefaultRouter

from .views import AlertThresholdViewSet, AlertViewSet

router = DefaultRouter()
router.register("thresholds", AlertThresholdViewSet, basename="alert-threshold")
router.register("events", AlertViewSet, basename="alert-event")

urlpatterns = router.urls
