from django.contrib import admin

from .models import AIInsight


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "device", "metric", "hours", "status", "created_at", "completed_at")
    list_filter = ("status", "created_at")
    search_fields = ("owner__username", "device__name", "metric", "response")
    readonly_fields = ("created_at", "completed_at")
