from django.contrib import admin

from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "is_active", "last_seen_at", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "owner__username", "api_key")
    readonly_fields = ("api_key", "created_at", "last_seen_at")
