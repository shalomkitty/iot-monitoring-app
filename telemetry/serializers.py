from django.utils import timezone
from rest_framework import serializers

from .models import TelemetryPoint


class TelemetryIngestSerializer(serializers.Serializer):
    metric = serializers.CharField(max_length=80)
    value = serializers.FloatField()
    unit = serializers.CharField(max_length=32, required=False, allow_blank=True)
    timestamp = serializers.DateTimeField(required=False)
    raw_payload = serializers.JSONField(required=False)

    def validate_metric(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("Metric name cannot be empty.")
        return value

    def validate(self, attrs):
        attrs.setdefault("timestamp", timezone.now())
        attrs.setdefault("unit", "")
        attrs.setdefault("raw_payload", {})
        return attrs


class TelemetryPointSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)

    class Meta:
        model = TelemetryPoint
        fields = (
            "id",
            "device",
            "device_name",
            "metric",
            "value",
            "unit",
            "timestamp",
            "raw_payload",
            "created_at",
        )
        read_only_fields = fields
