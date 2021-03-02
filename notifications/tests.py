from django.db.models.functions import text
import pytest
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from .models import NotificationType, Notification

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    User = get_user_model()
    user = User.objects.create(email="test@email.com", username="test")
    return user


@pytest.fixture
def profile(user):
    return user.profile


@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestModels:
    def test_profile_on_user_created(self):
        User = get_user_model()
        user = User.objects.create(email="test@email.com", username="test")

        assert hasattr(user, "profile")

    def test_profile_email_check_constraint(self, user):
        profile = user.profile
        profile.email = ""
        profile.notification_type = NotificationType.EMAIL

        with pytest.raises(IntegrityError):
            profile.save()

    def test_profile_sms_check_constraint(self, user):
        profile = user.profile
        profile.phone = ""
        profile.notification_type = NotificationType.SMS

        with pytest.raises(IntegrityError):
            profile.save()


class TestNotificationPreferencesAPI:
    def test_get_notification_preferences(self, profile, client):
        email = "test@email.com"
        phone = "+18092224444"

        profile.email = email
        profile.phone = phone
        profile.notification_type = NotificationType.EMAIL
        profile.save()

        response = client.get(reverse("notification-preferences"))
        assert response.status_code == 200

        response = response.json()
        assert response["email"] == email
        assert response["phone"] == phone
        assert response["notification_type"] == NotificationType.EMAIL

    def test_update_notification_preferences_email(self, profile, client):
        email = "test@email.com"

        assert profile.email is None
        assert profile.notification_type == NotificationType.NONE

        response = client.put(
            reverse("notification-preferences"),
            data={"email": email, "notification_type": NotificationType.EMAIL},
        )
        assert response.status_code == 200

        response = response.json()
        assert response["email"] == email
        assert response["notification_type"] == NotificationType.EMAIL

    def test_update_notification_email(self, profile, client):
        email = "test@email.com"
        email2 = "test2@email.com"

        profile.email = email
        profile.notification_type = NotificationType.EMAIL
        profile.save()

        response = client.put(
            reverse("notification-preferences"),
            data={
                "email": email2,
            },
        )
        assert response.status_code == 200

        response = response.json()
        assert response["email"] == email2

    def test_update_notification_preferences_sms(self, profile, client):
        phone = "+18092224444"

        assert profile.phone is None
        assert profile.notification_type == NotificationType.NONE

        response = client.put(
            reverse("notification-preferences"),
            data={"phone": phone, "notification_type": NotificationType.SMS},
        )
        assert response.status_code == 200

        response = response.json()
        assert response["phone"] == phone
        assert response["notification_type"] == NotificationType.SMS

    def test_update_notification_phone(self, profile, client):
        phone = "+18092224444"
        phone2 = "+18092225555"

        profile.phone = phone
        profile.notification_type = NotificationType.SMS
        profile.save()

        response = client.put(
            reverse("notification-preferences"),
            data={"phone": phone2},
        )
        assert response.status_code == 200

        response = response.json()
        assert response["phone"] == phone2

    def test_change_notification_preference(self, profile, client):
        profile.email = "test@email.com"
        profile.phone = "+18092224444"
        profile.notification_type = NotificationType.SMS
        profile.save()

        response = client.put(
            reverse("notification-preferences"),
            data={"notification_type": "email"},
        )
        assert response.status_code == 200

        response = response.json()
        assert response["notification_type"] == "email"


class TestNotificationsAPI:
    def test_create_notification(self, user, client):
        assert user.notifications.count() == 0

        now = timezone.now()
        response = client.post(
            reverse("notifications"),
            data={
                "title": "test title",
                "text": "text",
                "send_at": now.isoformat(),
            },
        )

        assert response.status_code == 201
        assert user.notifications.count() == 1

    def test_list_notifications(self, user, client):
        for _ in range(5):
            Notification.objects.create(user=user, title="title", text="test")

        response = client.get(
            reverse("notifications"),
        )
        assert response.status_code == 200

        response = response.json()
        assert len(response) == 5
