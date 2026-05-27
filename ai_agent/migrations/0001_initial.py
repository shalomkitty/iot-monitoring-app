# Generated manually for the educational project scaffold.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("devices", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AIInsight",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("metric", models.CharField(blank=True, max_length=80)),
                ("hours", models.PositiveIntegerField(default=24)),
                ("prompt", models.TextField()),
                ("response", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")], default="pending", max_length=20)),
                ("error", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("device", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="ai_insights", to="devices.device")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_insights", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="aiinsight",
            index=models.Index(fields=["owner", "-created_at"], name="ai_owner_created_idx"),
        ),
        migrations.AddIndex(
            model_name="aiinsight",
            index=models.Index(fields=["status", "-created_at"], name="ai_status_created_idx"),
        ),
    ]
