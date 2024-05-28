from rest_framework import serializers
from .models import (
    CustomUser,
    UserPreferences,
    EventTime,
    UserDigest,
)

import logging

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

    def validate_email(self, value):
        # Check if the instance is being updated and if the email has not changed
        if self.instance and self.instance.email == value:
            return value
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserPreferencesSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = UserPreferences
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["user"] = UserSerializer(read_only=True)
        return super(UserPreferencesSerializer, self).to_representation(instance)


class EventTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTime
        fields = "__all__"


class UserDigestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source="user", write_only=True
    )
    send_time = EventTimeSerializer(read_node=True)
    send_time_id = serializers.PrimaryKeyRelatedField(
        queryset=EventTime.objects.all(), source="send_time", write_only=True
    )

    class Meta:
        model = UserDigest
        fields = "__all__" + ("user_id", "send_time_id")

    def to_representation(self, instance):
        # This override is no longer necessary if using the setup above.
        return super(UserDigestSerializer, self).to_representation(instance)
