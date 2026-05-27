from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from alerts.models import Alert, AlertThreshold
from devices.models import Device
from telemetry.models import TelemetryPoint

User = get_user_model()


def test_ingest_telemetry_creates_alert(db):
    user = User.objects.create_user(username="owner", password="strong-password")
    device = Device.objects.create(owner=user, name="sensor-1")
    AlertThreshold.objects.create(
        owner=user,
        device=device,
        metric="temperature",
        max_value=30.0,
    )

    client = APIClient()
    response = client.post(
        reverse("telemetry-ingest"),
        {"metric": "temperature", "value": 31.5, "unit": "C"},
        format="json",
        HTTP_X_DEVICE_KEY=device.api_key,
    )

    assert response.status_code == 201
    assert TelemetryPoint.objects.count() == 1
    assert Alert.objects.count() == 1
    assert Alert.objects.first().status == Alert.Status.OPEN


def test_user_cannot_read_other_user_device(db):
    owner = User.objects.create_user(username="owner", password="strong-password")
    other = User.objects.create_user(username="other", password="strong-password")
    Device.objects.create(owner=owner, name="sensor-1")

    client = APIClient()
    client.force_authenticate(user=other)
    response = client.get("/api/devices/")

    assert response.status_code == 200
    assert response.data["count"] == 0
