# Generated manually for the educational project scaffold.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("devices", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TelemetryPoint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("metric", models.CharField(max_length=80)),
                ("value", models.FloatField()),
                ("unit", models.CharField(blank=True, max_length=32)),
                ("timestamp", models.DateTimeField()),
                ("raw_payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="telemetry_points", to="devices.device")),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
        migrations.AddIndex(
            model_name="telemetrypoint",
            index=models.Index(fields=["device", "-timestamp"], name="telemetry_device_time_idx"),
        ),
        migrations.AddIndex(
            model_name="telemetrypoint",
            index=models.Index(fields=["device", "metric", "-timestamp"], name="telemetry_dev_metric_time_idx"),
        ),
        migrations.AddIndex(
            model_name="telemetrypoint",
            index=models.Index(fields=["metric", "-timestamp"], name="telemetry_metric_time_idx"),
        ),
    ]
