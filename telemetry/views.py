from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from alerts.services import evaluate_thresholds_for_point
from devices.models import Device

from .models import TelemetryPoint
from .serializers import TelemetryIngestSerializer, TelemetryPointSerializer


class TelemetryIngestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        api_key = request.headers.get("X-DEVICE-KEY")
        if not api_key:
            return Response({"detail": "X-DEVICE-KEY header is required."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            device = Device.objects.get(api_key=api_key, is_active=True)
        except Device.DoesNotExist:
            return Response({"detail": "Invalid or inactive device key."}, status=status.HTTP_403_FORBIDDEN)

        many = isinstance(request.data, list)
        serializer = TelemetryIngestSerializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)

        items = serializer.validated_data if many else [serializer.validated_data]
        created_points = []
        alert_count = 0

        with transaction.atomic():
            for item in items:
                point = TelemetryPoint.objects.create(
                    device=device,
                    metric=item["metric"],
                    value=item["value"],
                    unit=item.get("unit", ""),
                    timestamp=item["timestamp"],
                    raw_payload=item.get("raw_payload", {}),
                )
                created_points.append(point)
                alert_count += len(evaluate_thresholds_for_point(point))

            device.last_seen_at = timezone.now()
            device.save(update_fields=["last_seen_at"])

        return Response(
            {
                "created": len(created_points),
                "point_ids": [point.id for point in created_points],
                "alerts_created": alert_count,
            },
            status=status.HTTP_201_CREATED,
        )


class TelemetryPointViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TelemetryPointSerializer
    ordering_fields = ["timestamp", "created_at", "metric", "value"]
    ordering = ["-timestamp"]
    filterset_fields = ["device", "metric"]

    def get_queryset(self):
        queryset = TelemetryPoint.objects.select_related("device", "device__owner")
        if not self.request.user.is_staff:
            queryset = queryset.filter(device__owner=self.request.user)

        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")

        if start:
            parsed_start = parse_datetime(start)
            if parsed_start:
                queryset = queryset.filter(timestamp__gte=parsed_start)

        if end:
            parsed_end = parse_datetime(end)
            if parsed_end:
                queryset = queryset.filter(timestamp__lte=parsed_end)

        return queryset
