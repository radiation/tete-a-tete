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
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    send_time = serializers.PrimaryKeyRelatedField(queryset=EventTime.objects.all())

    class Meta:
        model = UserDigest
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["user"] = UserSerializer(read_only=True)
        self.fields["send_time"] = EventTimeSerializer(read_only=True)
        return super(UserDigestSerializer, self).to_representation(instance)
