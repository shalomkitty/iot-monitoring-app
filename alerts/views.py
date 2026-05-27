from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Alert, AlertThreshold
from .serializers import AlertSerializer, AlertThresholdSerializer


class AlertThresholdViewSet(viewsets.ModelViewSet):
    serializer_class = AlertThresholdSerializer

    def get_queryset(self):
        queryset = AlertThreshold.objects.select_related("owner", "device")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AlertSerializer
    filterset_fields = ["device", "status", "threshold"]
    ordering_fields = ["triggered_at", "status"]
    ordering = ["-triggered_at"]

    def get_queryset(self):
        queryset = Alert.objects.select_related("threshold", "device", "telemetry_point")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(device__owner=self.request.user)

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = Alert.Status.ACKNOWLEDGED
        alert.acknowledged_at = timezone.now()
        alert.save(update_fields=["status", "acknowledged_at"])
        return Response(AlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        alert = self.get_object()
        alert.status = Alert.Status.CLOSED
        alert.closed_at = timezone.now()
        alert.save(update_fields=["status", "closed_at"])
        return Response(AlertSerializer(alert).data)
