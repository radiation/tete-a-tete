from rest_framework import serializers
from .models import (
    CustomUser,
    UserPreferences,
    EventTime,
    Meeting,
    MeetingRecurrence,
    MeetingAttendee,
    Task,
    MeetingTask,
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


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(MeetingSerializer, self).to_representation(instance)
        recurrence_id = (
            instance["recurrence"]
            if isinstance(instance, dict)
            else instance.recurrence
        )
        ret["recurrence"] = MeetingRecurrenceSerializer(recurrence_id).data
        return ret


class MeetingRecurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRecurrence
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Task
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(TaskSerializer, self).to_representation(instance)
        assignee_email = (
            instance["assignee"] if isinstance(instance, dict) else instance.assignee
        )
        ret["assignee"] = UserSerializer(assignee_email).data
        return ret


class MeetingTaskSerializer(serializers.ModelSerializer):
    meeting = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.all())
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())

    class Meta:
        model = MeetingTask
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(MeetingTaskSerializer, self).to_representation(instance)
        if isinstance(instance, dict):
            meeting_id = instance["meeting"]
            task_id = instance["task"]
        else:
            meeting_id = instance.meeting
            task_id = instance.task
        ret["meeting"] = MeetingSerializer(meeting_id).data
        ret["task"] = TaskSerializer(task_id).data
        return ret


class MeetingAttendeeSerializer(serializers.ModelSerializer):
    meeting = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = MeetingAttendee
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(MeetingAttendeeSerializer, self).to_representation(instance)
        if isinstance(instance, dict):
            meeting_id = instance["meeting"]
            user_id = instance["user"]
        else:
            meeting_id = instance.meeting
            user_id = instance.user
        ret["meeting"] = MeetingSerializer(meeting_id).data
        ret["user"] = UserSerializer(user_id).data
        return ret


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
