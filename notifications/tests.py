import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from .models import NotificationType

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    User = get_user_model()
    user = User.objects.create(email="test@email.com", username="test")
    return user


def test_profile_on_user_created():
    User = get_user_model()
    user = User.objects.create(email="test@email.com", username="test")

    assert hasattr(user, "profile")


def test_profile_email_check_constraint(user):
    profile = user.profile
    profile.email = ""
    profile.notification_type = NotificationType.EMAIL

    with pytest.raises(IntegrityError):
        profile.save()


def test_profile_sms_check_constraint(user):
    profile = user.profile
    profile.phone = ""
    profile.notification_type = NotificationType.SMS

    with pytest.raises(IntegrityError):
        profile.save()
