from rest_framework import serializers
from common.models import EventTime
from users.models import CustomUser
from users.serializers import UserSerializer
from restapi.models import (
    Meeting,
    MeetingRecurrence,
    MeetingAttendee,
    Task,
    MeetingTask,
)

import logging

logger = logging.getLogger(__name__)


class EventTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTime
        fields = "__all__"


class MeetingSerializer(serializers.ModelSerializer):
    recurrence = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = "__all__"

    def get_recurrence(self, obj):
        if isinstance(obj, dict):
            recurrence = obj.get("recurrence", None)
        else:
            recurrence = getattr(obj, "recurrence", None)

        if recurrence:
            return MeetingRecurrenceSerializer(recurrence).data
        return None


class MeetingRecurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRecurrence
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    assignee_detail = serializers.SerializerMethodField()
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Task
        fields = "__all__"

    def get_assignee_detail(self, obj):
        if isinstance(obj, dict):
            assignee = obj.get("assignee", None)
        else:
            assignee = getattr(obj, "assignee", None)

        if assignee:
            return UserSerializer(assignee).data
        return None


class MeetingTaskSerializer(serializers.ModelSerializer):
    meeting = serializers.PrimaryKeyRelatedField(
        queryset=Meeting.objects.all(), write_only=True, allow_null=False
    )
    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), write_only=True, allow_null=False
    )
    meeting_detail = MeetingSerializer(source="meeting", read_only=True)
    task_detail = TaskSerializer(source="task", read_only=True)

    class Meta:
        model = MeetingTask
        fields = "__all__"
        extra_kwargs = {"meeting": {"write_only": True}, "task": {"write_only": True}}


class MeetingAttendeeSerializer(serializers.ModelSerializer):
    meeting = serializers.PrimaryKeyRelatedField(
        queryset=Meeting.objects.all(), write_only=True, allow_null=False
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), write_only=True, allow_null=False
    )
    meeting_detail = MeetingSerializer(source="meeting", read_only=True)
    user_detail = UserSerializer(source="user", read_only=True)

    class Meta:
        model = MeetingAttendee
        fields = ["meeting", "user", "meeting_detail", "user_detail", "is_scheduler"]
        extra_kwargs = {"meeting": {"write_only": True}, "user": {"write_only": True}}
