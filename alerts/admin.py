from django.contrib import admin

from .models import Alert, AlertThreshold


@admin.register(AlertThreshold)
class AlertThresholdAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "device", "metric", "min_value", "max_value", "enabled")
    list_filter = ("enabled", "metric")
    search_fields = ("metric", "owner__username", "device__name")


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("id", "device", "status", "message", "triggered_at")
    list_filter = ("status", "triggered_at")
    search_fields = ("message", "device__name", "threshold__metric")
    readonly_fields = ("triggered_at",)
