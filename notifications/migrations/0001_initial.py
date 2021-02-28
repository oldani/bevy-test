# Generated by Django 3.1 on 2021-02-28 23:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("email", "Email"),
                            ("sms", "Sms"),
                            ("", "None"),
                        ],
                        default="",
                        max_length=8,
                    ),
                ),
                ("email", models.EmailField(max_length=254, null=True)),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, null=True, region=None
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("title", models.CharField(max_length=256)),
                ("text", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("send_at", models.DateTimeField(null=True)),
                ("sent_at", models.DateTimeField(null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="profile",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        models.Q(
                            ("email__isnull", False),
                            ("email__length__gt", 0),
                            ("notification_type", "email"),
                        ),
                        models.Q(
                            ("notification_type", "sms"),
                            ("phone__isnull", False),
                            ("phone__length__gt", 0),
                        ),
                        ("notification_type", ""),
                        _connector="OR",
                    )
                ),
                name="notifications_profile_notification_type",
            ),
        ),
    ]