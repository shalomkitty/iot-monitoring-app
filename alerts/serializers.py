from rest_framework import serializers

from devices.models import Device

from .models import Alert, AlertThreshold


class AlertThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertThreshold
        fields = (
            "id",
            "device",
            "metric",
            "min_value",
            "max_value",
            "enabled",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate_metric(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("Metric name cannot be empty.")
        return value

    def validate_device(self, value):
        request = self.context["request"]
        if value is not None and not request.user.is_staff and value.owner_id != request.user.id:
            raise serializers.ValidationError("You can create thresholds only for your own devices.")
        return value

    def validate(self, attrs):
        if attrs.get("min_value") is None and attrs.get("max_value") is None:
            raise serializers.ValidationError("At least one of min_value or max_value is required.")
        min_value = attrs.get("min_value")
        max_value = attrs.get("max_value")
        if min_value is not None and max_value is not None and min_value >= max_value:
            raise serializers.ValidationError("min_value must be lower than max_value.")
        return attrs


class AlertSerializer(serializers.ModelSerializer):
    metric = serializers.CharField(source="threshold.metric", read_only=True)
    value = serializers.FloatField(source="telemetry_point.value", read_only=True)
    device_name = serializers.CharField(source="device.name", read_only=True)

    class Meta:
        model = Alert
        fields = (
            "id",
            "threshold",
            "device",
            "device_name",
            "metric",
            "value",
            "telemetry_point",
            "status",
            "message",
            "triggered_at",
            "acknowledged_at",
            "closed_at",
        )
        read_only_fields = fields
