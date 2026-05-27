# Generated manually for the educational project scaffold.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("devices", "0001_initial"),
        ("telemetry", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AlertThreshold",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("metric", models.CharField(max_length=80)),
                ("min_value", models.FloatField(blank=True, null=True)),
                ("max_value", models.FloatField(blank=True, null=True)),
                ("enabled", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("device", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="alert_thresholds", to="devices.device")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alert_thresholds", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["metric"],
            },
        ),
        migrations.CreateModel(
            name="Alert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("open", "Open"), ("acknowledged", "Acknowledged"), ("closed", "Closed")], default="open", max_length=20)),
                ("message", models.CharField(max_length=255)),
                ("triggered_at", models.DateTimeField(auto_now_add=True)),
                ("acknowledged_at", models.DateTimeField(blank=True, null=True)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alerts", to="devices.device")),
                ("telemetry_point", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alerts", to="telemetry.telemetrypoint")),
                ("threshold", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alerts", to="alerts.alertthreshold")),
            ],
            options={
                "ordering": ["-triggered_at"],
            },
        ),
        migrations.AddIndex(
            model_name="alertthreshold",
            index=models.Index(fields=["owner", "metric"], name="threshold_owner_metric_idx"),
        ),
        migrations.AddIndex(
            model_name="alertthreshold",
            index=models.Index(fields=["device", "metric"], name="threshold_device_metric_idx"),
        ),
        migrations.AddIndex(
            model_name="alert",
            index=models.Index(fields=["device", "status", "-triggered_at"], name="alert_device_status_time_idx"),
        ),
        migrations.AddIndex(
            model_name="alert",
            index=models.Index(fields=["status", "-triggered_at"], name="alert_status_time_idx"),
        ),
        migrations.AddConstraint(
            model_name="alert",
            constraint=models.UniqueConstraint(fields=("threshold", "telemetry_point"), name="unique_alert_per_threshold_point"),
        ),
    ]
