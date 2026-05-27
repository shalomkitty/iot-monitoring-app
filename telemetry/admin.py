from django.contrib import admin

from .models import TelemetryPoint


@admin.register(TelemetryPoint)
class TelemetryPointAdmin(admin.ModelAdmin):
    list_display = ("id", "device", "metric", "value", "unit", "timestamp", "created_at")
    list_filter = ("metric", "timestamp", "created_at")
    search_fields = ("device__name", "metric")
    readonly_fields = ("created_at",)
