# Generated manually for the educational project scaffold.

import devices.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Device",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("api_key", models.CharField(default=devices.models.generate_api_key, editable=False, max_length=96, unique=True)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("last_seen_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="devices", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddIndex(
            model_name="device",
            index=models.Index(fields=["owner", "name"], name="device_owner_name_idx"),
        ),
        migrations.AddIndex(
            model_name="device",
            index=models.Index(fields=["api_key"], name="device_api_key_idx"),
        ),
    ]
