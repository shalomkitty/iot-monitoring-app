from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone

from telemetry.models import TelemetryPoint

from .models import AIInsight


def build_prompt(insight: AIInsight, stats: dict, latest: TelemetryPoint | None) -> str:
    device_part = f"device_id={insight.device_id}" if insight.device_id else "all user devices"
    metric_part = insight.metric if insight.metric else "all metrics"
    latest_part = "none"
    if latest is not None:
        latest_part = f"{latest.metric}={latest.value}{latest.unit} at {latest.timestamp.isoformat()}"

    return (
        "Analyze IoT telemetry and produce a concise operational summary. "
        f"Scope: {device_part}; metric: {metric_part}; period: last {insight.hours} hours. "
        f"Stats: {stats}. Latest point: {latest_part}. "
        "Mention anomalies, possible risks, and practical next actions."
    )


def fallback_response(stats: dict, latest: TelemetryPoint | None) -> str:
    if stats["count"] == 0:
        return "No telemetry points were found for the selected period. No operational conclusion can be made."

    latest_text = ""
    if latest is not None:
        latest_text = f" Latest value: {latest.metric}={latest.value}{latest.unit}."

    return (
        "OPENAI_API_KEY is not configured, so the project returned a deterministic local summary. "
        f"Points: {stats['count']}; min={stats['min_value']}; avg={stats['avg_value']}; max={stats['max_value']}."
        f"{latest_text} Check configured thresholds and inspect recent device activity."
    )


@shared_task
def generate_ai_insight(insight_id: int) -> int:
    insight = AIInsight.objects.select_related("owner", "device").get(id=insight_id)

    try:
        since = timezone.now() - timedelta(hours=insight.hours)
        queryset = TelemetryPoint.objects.filter(device__owner=insight.owner, timestamp__gte=since)

        if insight.device_id:
            queryset = queryset.filter(device_id=insight.device_id)

        if insight.metric:
            queryset = queryset.filter(metric=insight.metric)

        stats = queryset.aggregate(
            count=Count("id"),
            min_value=Min("value"),
            avg_value=Avg("value"),
            max_value=Max("value"),
        )
        latest = queryset.order_by("-timestamp").first()
        prompt = build_prompt(insight, stats, latest)
        insight.prompt = prompt

        if settings.OPENAI_API_KEY:
            from openai import OpenAI

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an IoT monitoring assistant. Be concise and operational.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            response = completion.choices[0].message.content or ""
        else:
            response = fallback_response(stats, latest)

        insight.response = response
        insight.status = AIInsight.Status.COMPLETED
        insight.completed_at = timezone.now()
        insight.save(update_fields=["prompt", "response", "status", "completed_at"])
    except Exception as exc:
        insight.status = AIInsight.Status.FAILED
        insight.error = str(exc)
        insight.completed_at = timezone.now()
        insight.save(update_fields=["status", "error", "completed_at"])

    return insight.id
