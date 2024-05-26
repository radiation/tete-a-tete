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
    class Meta:
        model = Meeting
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if isinstance(instance, dict) and "recurrence" in instance:
            recurrence_id = instance["recurrence"]
            recurrence_instance = MeetingRecurrence.objects.get(id=recurrence_id)
            ret["recurrence"] = MeetingRecurrenceSerializer(recurrence_instance).data
        elif hasattr(instance, "recurrence") and instance.recurrence is not None:
            ret["recurrence"] = MeetingRecurrenceSerializer(instance.recurrence).data
        else:
            ret["recurrence"] = None

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
