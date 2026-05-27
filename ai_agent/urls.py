from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AIInsightViewSet, GenerateInsightView

router = DefaultRouter()
router.register("insights", AIInsightViewSet, basename="ai-insight")

urlpatterns = [
    path("insights/generate/", GenerateInsightView.as_view(), name="generate-ai-insight"),
]
urlpatterns += router.urls
