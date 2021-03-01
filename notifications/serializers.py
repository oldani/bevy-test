from django.db import IntegrityError
from rest_framework import serializers

from .models import Profile, NotificationType


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "notification_type", "email", "phone")
        read_only_fields = ("id",)

    def update(self, profile, validated_data):
        profile.notification_type = validated_data.get(
            "notification_type", profile.notification_type
        )
        profile.email = validated_data.get("email", profile.email)
        profile.phone = validated_data.get("phone", profile.phone)

        try:
            profile.save()
        except IntegrityError as error:
            if (
                "notifications_profile_notification_type"
                not in error.__cause__.__str__()
            ):
                raise

            if (
                profile.notification_type == NotificationType.EMAIL
                and not profile.email
            ):
                raise serializers.ValidationError("Missing email field")
            elif (
                profile.notification_type == NotificationType.SMS
                and not profile.phone
            ):
                raise serializers.ValidationError("Missing phone field")

        return profile
