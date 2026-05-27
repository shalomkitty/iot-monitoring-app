from django.conf import settings
from django.db import models

from devices.models import Device


class AIInsight(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_insights")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="ai_insights", null=True, blank=True)
    metric = models.CharField(max_length=80, blank=True)
    hours = models.PositiveIntegerField(default=24)
    prompt = models.TextField()
    response = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "-created_at"], name="ai_owner_created_idx"),
            models.Index(fields=["status", "-created_at"], name="ai_status_created_idx"),
        ]

    def __str__(self) -> str:
        return f"AI insight #{self.id} ({self.status})"
