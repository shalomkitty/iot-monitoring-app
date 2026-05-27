import secrets

from django.conf import settings
from django.db import models


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)


class Device(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(max_length=120)
    api_key = models.CharField(max_length=96, unique=True, default=generate_api_key, editable=False)
    location = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["owner", "name"], name="device_owner_name_idx"),
            models.Index(fields=["api_key"], name="device_api_key_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.owner})"

    def rotate_api_key(self) -> None:
        self.api_key = generate_api_key()
        self.save(update_fields=["api_key"])
