from django.conf import settings
from django.db import models

from devices.models import Device
from telemetry.models import TelemetryPoint


class AlertThreshold(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="alert_thresholds")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="alert_thresholds", null=True, blank=True)
    metric = models.CharField(max_length=80)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["metric"]
        indexes = [
            models.Index(fields=["owner", "metric"], name="threshold_owner_metric_idx"),
            models.Index(fields=["device", "metric"], name="threshold_device_metric_idx"),
        ]

    def __str__(self) -> str:
        scope = self.device_id if self.device_id else "all-devices"
        return f"{scope}:{self.metric}"

    def is_breached(self, value: float) -> bool:
        if self.min_value is not None and value < self.min_value:
            return True
        if self.max_value is not None and value > self.max_value:
            return True
        return False


class Alert(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        CLOSED = "closed", "Closed"

    threshold = models.ForeignKey(AlertThreshold, on_delete=models.CASCADE, related_name="alerts")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="alerts")
    telemetry_point = models.ForeignKey(TelemetryPoint, on_delete=models.CASCADE, related_name="alerts")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    message = models.CharField(max_length=255)
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-triggered_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["threshold", "telemetry_point"],
                name="unique_alert_per_threshold_point",
            )
        ]
        indexes = [
            models.Index(fields=["device", "status", "-triggered_at"], name="alert_device_status_time_idx"),
            models.Index(fields=["status", "-triggered_at"], name="alert_status_time_idx"),
        ]

    def __str__(self) -> str:
        return self.message
