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
    meeting = MeetingSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    meeting_id = serializers.PrimaryKeyRelatedField(
        queryset=Meeting.objects.all(), source="meeting", write_only=True
    )
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source="task",
        write_only=True,
    )

    class Meta:
        model = MeetingTask
        fields = "__all__"


class MeetingAttendeeSerializer(serializers.ModelSerializer):
    meeting = MeetingSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    meeting_id = serializers.PrimaryKeyRelatedField(
        queryset=Meeting.objects.all(), source="meeting", write_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = MeetingAttendee
        fields = "__all__"
