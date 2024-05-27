from django.db import connections
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import AsyncModelViewSet
from .models import *
from .serializers import *
from .services import task_service
from .tasks import *

import logging

logger = logging.getLogger(__name__)


# For looking up related models
RELATIONS_MODEL_MAPPING = {
    "assignee": CustomUser,
    "meeting": Meeting,
    "task": Task,
    "user": CustomUser,
}

MODEL_SERIALIZER_MAPPING = {
    Task: TaskSerializer,
    MeetingAttendee: MeetingAttendeeSerializer,
}


class MeetingViewSet(AsyncModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    def get_serializer_class(self):
        return self.serializer_class

    # Returns a MeetingRecurrence object
    @action(detail=False, methods=["GET"])
    def get_meeting_recurrence(self, request):
        meeting_id = request.query_params.get("meeting_id")
        recurrence = MeetingRecurrence.objects.get(meeting__id=meeting_id)
        return Response(recurrence)

    # Returns a Meeting object
    @action(detail=False, methods=["GET"])
    def get_next_occurrence(self, request):
        meeting_id = request.query_params.get("meeting_id")
        meeting = Meeting.objects.get(pk=meeting_id)
        next_occurrence = meeting.get_next_occurrence()
        return Response(next_occurrence)

    # Move tasks and agenda items to the next occurrence
    @action(detail=False, methods=["POST"])
    def complete(self, request):
        meeting_service.complete_meeting(request.data.get("meeting_id"))
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def add_recurrence(self, request, pk=None):
        meeting = self.get_object()
        recurrence_id = request.data.get("recurrence")

        # Fetch the existing MeetingRecurrence instance
        if recurrence_id is not None:
            recurrence = get_object_or_404(MeetingRecurrence, pk=recurrence_id)

            # Associate the existing MeetingRecurrence with the Meeting
            meeting.recurrence = recurrence
            meeting.save()

            # Dispatch the update task to Celery
            meeting_serializer = self.get_serializer(meeting)
            self.dispatch_task(meeting_serializer, create=False)

            return Response(
                {"message": "Meeting recurrence update dispatched"},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(
                {"message": "Recurrence ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeetingRecurrenceViewSet(AsyncModelViewSet):
    queryset = MeetingRecurrence.objects.all()
    serializer_class = MeetingRecurrenceSerializer


class TaskViewSet(AsyncModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=["GET"])
    def list_by_user(self, request):
        user_id = request.query_params.get("user_id")
        tasks = Task.objects.filter(assignee__id=user_id)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"])
    def mark_complete(self, request):
        task_service.mark_task_complete(request.data.get("task_id"))
        return Response(status=status.HTTP_200_OK)


class MeetingTaskViewSet(AsyncModelViewSet):
    queryset = MeetingTask.objects.all()
    serializer_class = MeetingTaskSerializer

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=["GET"])
    def list_tasks_by_meeting(self, request):
        return self.list_by_meeting(request, Task)


class MeetingAttendeeViewSet(AsyncModelViewSet):
    queryset = MeetingAttendee.objects.all()
    serializer_class = MeetingAttendeeSerializer

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=["GET"])
    def list_attendees_by_meeting(self, request):
        return self.list_by_meeting(request, Task)

    @action(detail=False, methods=["GET"])
    def list_meetings_by_user(self, request):
        user_id = request.query_params.get("user_id")
        queryset = Meeting.objects.filter(
            Q(scheduler__id=user_id) | Q(attendee__id=user_id)
        ).order_by("start_date")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
