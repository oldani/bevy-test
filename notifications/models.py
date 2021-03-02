from uuid import uuid4
from django.conf import settings
from django.db import models
from django.db.models.functions import Length

from phonenumber_field.modelfields import PhoneNumberField


class NotificationType(models.TextChoices):
    EMAIL = "email"
    SMS = "sms"
    NONE = ""


models.CharField.register_lookup(Length)


class Profile(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    notification_type = models.CharField(
        max_length=8,
        default=NotificationType.NONE,
        choices=NotificationType.choices,
    )
    email = models.EmailField(null=True)
    phone = PhoneNumberField(null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_notification_type",
                check=models.Q(
                    models.Q(
                        notification_type=NotificationType.EMAIL,
                        email__isnull=False,
                        email__length__gt=0,
                    )
                    | models.Q(
                        notification_type=NotificationType.SMS,
                        phone__isnull=False,
                        phone__length__gt=0,
                    )
                    | models.Q(notification_type="")
                ),
            )
        ]


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(max_length=256)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    send_at = models.DateTimeField(null=True)
    sent_at = models.DateTimeField(null=True)
