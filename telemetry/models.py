from django.db import models

from devices.models import Device


class TelemetryPoint(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="telemetry_points")
    metric = models.CharField(max_length=80)
    value = models.FloatField()
    unit = models.CharField(max_length=32, blank=True)
    timestamp = models.DateTimeField()
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["device", "-timestamp"], name="telemetry_device_time_idx"),
            models.Index(fields=["device", "metric", "-timestamp"], name="telemetry_dev_metric_time_idx"),
            models.Index(fields=["metric", "-timestamp"], name="telemetry_metric_time_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.device_id} {self.metric}={self.value} at {self.timestamp}"
