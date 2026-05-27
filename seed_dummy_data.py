"""Seed dummy data for the IoT Monitoring API project.

Place this file in the project root, next to manage.py, then run:
    python seed_dummy_data.py
"""

from __future__ import annotations

import os
import random
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iot_monitoring.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.utils import timezone  # noqa: E402
from rest_framework.authtoken.models import Token  # noqa: E402

from ai_agent.models import AIInsight  # noqa: E402
from alerts.models import AlertThreshold  # noqa: E402
from alerts.services import evaluate_thresholds_for_point  # noqa: E402
from devices.models import Device  # noqa: E402
from telemetry.models import TelemetryPoint  # noqa: E402

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo12345"
ADMIN_USERNAME = "iot_admin"
ADMIN_PASSWORD = "admin12345"

random.seed(42)


def create_users():
    User = get_user_model()

    owner, _ = User.objects.get_or_create(
        username=DEMO_USERNAME,
        defaults={
            "email": "demo@example.com",
            "first_name": "Demo",
            "last_name": "User",
        },
    )
    owner.email = "demo@example.com"
    owner.first_name = "Demo"
    owner.last_name = "User"
    owner.set_password(DEMO_PASSWORD)
    owner.save()

    admin, _ = User.objects.get_or_create(
        username=ADMIN_USERNAME,
        defaults={
            "email": "iot.admin@example.com",
            "first_name": "IoT",
            "last_name": "Admin",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    admin.email = "iot.admin@example.com"
    admin.is_staff = True
    admin.is_superuser = True
    admin.set_password(ADMIN_PASSWORD)
    admin.save()

    Token.objects.filter(user=owner).delete()
    token = Token.objects.create(user=owner)

    return owner, admin, token


def reset_demo_data(owner):
    AIInsight.objects.filter(owner=owner).delete()
    AlertThreshold.objects.filter(owner=owner).delete()
    Device.objects.filter(owner=owner).delete()


def create_devices(owner):
    devices = {
        "lab": Device.objects.create(
            owner=owner,
            name="lab-sensor-01",
            api_key="dummy-lab-sensor-key",
            location="Laboratory room 204",
            metadata={
                "type": "environment_sensor",
                "firmware": "1.4.2",
                "protocol": "HTTP",
                "sampling_interval_seconds": 900,
            },
        ),
        "freezer": Device.objects.create(
            owner=owner,
            name="storage-freezer-01",
            api_key="dummy-freezer-key",
            location="Cold storage",
            metadata={
                "type": "industrial_freezer",
                "firmware": "2.1.0",
                "protocol": "HTTP",
                "sampling_interval_seconds": 900,
            },
        ),
        "office": Device.objects.create(
            owner=owner,
            name="office-air-01",
            api_key="dummy-office-air-key",
            location="Office floor 3",
            metadata={
                "type": "air_quality_sensor",
                "firmware": "1.9.5",
                "protocol": "HTTP",
                "sampling_interval_seconds": 900,
            },
        ),
    }
    return devices


def create_thresholds(owner, devices):
    return [
        AlertThreshold.objects.create(
            owner=owner,
            device=devices["lab"],
            metric="temperature",
            min_value=18.0,
            max_value=28.0,
        ),
        AlertThreshold.objects.create(
            owner=owner,
            device=devices["lab"],
            metric="humidity",
            min_value=35.0,
            max_value=70.0,
        ),
        AlertThreshold.objects.create(
            owner=owner,
            device=devices["freezer"],
            metric="temperature",
            min_value=-5.0,
            max_value=8.0,
        ),
        AlertThreshold.objects.create(
            owner=owner,
            device=devices["office"],
            metric="co2",
            max_value=900.0,
        ),
        AlertThreshold.objects.create(
            owner=owner,
            device=None,
            metric="battery",
            min_value=20.0,
        ),
    ]


def metric_value(device_key: str, metric: str, index: int) -> float:
    noise = random.uniform(-1.0, 1.0)

    if device_key == "lab":
        if metric == "temperature":
            value = 23.0 + random.uniform(-2.0, 2.0)
            if index in {20, 21, 58}:
                value = 31.5 + random.uniform(0.0, 2.0)
            return round(value, 2)
        if metric == "humidity":
            value = 52.0 + random.uniform(-8.0, 8.0)
            if index in {34, 35}:
                value = 28.0 + random.uniform(-2.0, 1.0)
            return round(value, 2)
        if metric == "battery":
            value = 86.0 - index * 0.18 + noise
            return round(max(value, 10.0), 2)

    if device_key == "freezer":
        if metric == "temperature":
            value = 3.0 + random.uniform(-1.5, 1.5)
            if index in {44, 45, 46, 47}:
                value = 10.0 + random.uniform(0.0, 2.5)
            return round(value, 2)
        if metric == "battery":
            value = 72.0 - index * 0.12 + noise
            return round(max(value, 10.0), 2)

    if device_key == "office":
        if metric == "temperature":
            return round(22.0 + random.uniform(-1.5, 1.5), 2)
        if metric == "humidity":
            return round(45.0 + random.uniform(-6.0, 6.0), 2)
        if metric == "co2":
            value = 620.0 + random.uniform(-80.0, 160.0)
            if index in {50, 51, 52, 53, 54}:
                value = 1100.0 + random.uniform(0.0, 250.0)
            return round(value, 2)
        if metric == "battery":
            value = 38.0 - index * 0.24 + noise
            return round(max(value, 8.0), 2)

    raise ValueError(f"Unsupported metric {metric!r} for device {device_key!r}")


def create_telemetry(devices):
    metric_units = {
        "temperature": "C",
        "humidity": "%",
        "battery": "%",
        "co2": "ppm",
    }
    device_metrics = {
        "lab": ["temperature", "humidity", "battery"],
        "freezer": ["temperature", "battery"],
        "office": ["temperature", "humidity", "co2", "battery"],
    }

    start = timezone.now() - timedelta(hours=24)
    created_count = 0
    alert_count = 0

    for i in range(96):
        timestamp = start + timedelta(minutes=15 * i)
        for device_key, metrics in device_metrics.items():
            device = devices[device_key]
            for metric in metrics:
                value = metric_value(device_key, metric, i)
                point = TelemetryPoint.objects.create(
                    device=device,
                    metric=metric,
                    value=value,
                    unit=metric_units[metric],
                    timestamp=timestamp,
                    raw_payload={
                        "source": "dummy-seed",
                        "sequence": i,
                        "quality": "simulated",
                    },
                )
                created_count += 1
                alert_count += len(evaluate_thresholds_for_point(point))

    for device in devices.values():
        device.last_seen_at = timezone.now()
        device.save(update_fields=["last_seen_at"])

    return created_count, alert_count


def create_ai_insights(owner, devices):
    now = timezone.now()

    AIInsight.objects.create(
        owner=owner,
        device=devices["lab"],
        metric="temperature",
        hours=24,
        prompt="Analyze the last 24 hours of lab temperature telemetry and identify anomalies.",
        response=(
            "The laboratory sensor shows a mostly stable temperature range, "
            "with several high-temperature spikes above the configured threshold. "
            "Recommended action: inspect ventilation and verify sensor calibration."
        ),
        status=AIInsight.Status.COMPLETED,
        completed_at=now,
    )

    AIInsight.objects.create(
        owner=owner,
        device=devices["office"],
        metric="co2",
        hours=24,
        prompt="Summarize CO2 anomalies for the office air-quality sensor.",
        response=(
            "CO2 values exceeded the configured limit during a continuous interval. "
            "Recommended action: increase ventilation and check occupancy levels."
        ),
        status=AIInsight.Status.COMPLETED,
        completed_at=now,
    )

    AIInsight.objects.create(
        owner=owner,
        device=None,
        metric="battery",
        hours=24,
        prompt="Find devices with low battery risk.",
        status=AIInsight.Status.PENDING,
    )


def main():
    owner, admin, token = create_users()
    reset_demo_data(owner)
    devices = create_devices(owner)
    thresholds = create_thresholds(owner, devices)
    telemetry_count, alert_count = create_telemetry(devices)
    create_ai_insights(owner, devices)

    print("Dummy data inserted successfully.")
    print(f"Demo API user: {DEMO_USERNAME} / {DEMO_PASSWORD}")
    print(f"Demo API token: {token.key}")
    print(f"Admin user: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    print("Device API keys:")
    for device in devices.values():
        print(f"  {device.name}: {device.api_key}")
    print(f"Devices: {len(devices)}")
    print(f"Thresholds: {len(thresholds)}")
    print(f"Telemetry points: {telemetry_count}")
    print(f"Alerts created: {alert_count}")
    print("AI insight records: 3")


if __name__ == "__main__":
    main()
