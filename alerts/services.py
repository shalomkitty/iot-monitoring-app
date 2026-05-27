from django.db.models import Q

from .models import Alert, AlertThreshold


def build_alert_message(threshold: AlertThreshold, value: float) -> str:
    if threshold.max_value is not None and value > threshold.max_value:
        return f"{threshold.metric}={value} is above max threshold {threshold.max_value}."
    if threshold.min_value is not None and value < threshold.min_value:
        return f"{threshold.metric}={value} is below min threshold {threshold.min_value}."
    return f"{threshold.metric}={value} breached threshold."


def evaluate_thresholds_for_point(point):
    thresholds = (
        AlertThreshold.objects
        .filter(owner=point.device.owner, enabled=True, metric=point.metric)
        .filter(Q(device=point.device) | Q(device__isnull=True))
    )

    created_alerts = []
    for threshold in thresholds:
        if not threshold.is_breached(point.value):
            continue

        alert, created = Alert.objects.get_or_create(
            threshold=threshold,
            telemetry_point=point,
            defaults={
                "device": point.device,
                "message": build_alert_message(threshold, point.value),
            },
        )
        if created:
            created_alerts.append(alert)

    return created_alerts
