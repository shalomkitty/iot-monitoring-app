from rest_framework import serializers

from .models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = (
            "id",
            "name",
            "api_key",
            "location",
            "metadata",
            "is_active",
            "last_seen_at",
            "created_at",
        )
        read_only_fields = ("id", "api_key", "last_seen_at", "created_at")
