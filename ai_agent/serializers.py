from rest_framework import serializers

from devices.models import Device

from .models import AIInsight


class GenerateInsightSerializer(serializers.Serializer):
    device_id = serializers.IntegerField(required=False)
    metric = serializers.CharField(max_length=80, required=False, allow_blank=True)
    hours = serializers.IntegerField(min_value=1, max_value=720, default=24)

    def validate_metric(self, value):
        return value.strip().lower()

    def validate_device_id(self, value):
        request = self.context["request"]
        try:
            device = Device.objects.get(id=value)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Device does not exist.")

        if not request.user.is_staff and device.owner_id != request.user.id:
            raise serializers.ValidationError("You can request insights only for your own devices.")

        return value


class AIInsightSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)

    class Meta:
        model = AIInsight
        fields = (
            "id",
            "device",
            "device_name",
            "metric",
            "hours",
            "prompt",
            "response",
            "status",
            "error",
            "created_at",
            "completed_at",
        )
        read_only_fields = fields
