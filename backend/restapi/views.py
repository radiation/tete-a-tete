from django.db import connections
from django.db.utils import OperationalError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import AsyncModelViewSet
from restapi.models import (
    Meeting,
    MeetingRecurrence,
    MeetingAttendee,
    Task,
    MeetingTask,
)
from restapi.serializers import (
    MeetingSerializer,
    MeetingRecurrenceSerializer,
    TaskSerializer,
    MeetingTaskSerializer,
    MeetingAttendeeSerializer,
)
from restapi.services import MeetingService, TaskService
from users.models import CustomUser

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


def health(request):
    try:
        connections["default"].cursor()
    except OperationalError:
        return HttpResponse("Database unavailable", status=503)
    return HttpResponse("OK")


class MeetingViewSet(AsyncModelViewSet):
    serializer_class = MeetingSerializer

    # Return all Meeting objects with related MeetingRecurrence objects
    def get_queryset(self):
        return Meeting.objects.select_related("recurrence").all()

    # Return the serializer class
    def get_serializer_class(self):
        return self.serializer_class

    # Returns a MeetingRecurrence object
    @action(detail=False, methods=["GET"])
    def get_meeting_recurrence(self, request):
        meeting_id = request.query_params.get("meeting_id")
        recurrence = get_object_or_404(MeetingRecurrence, meeting__id=meeting_id)
        serializer = MeetingRecurrenceSerializer(recurrence)
        return Response(serializer.data)

    # Returns a Meeting object
    @action(detail=False, methods=["GET"])
    def get_next_occurrence(self, request):
        meeting_id = request.query_params.get("meeting_id")
        logger.debug(f"\n\nGetting next occurrence for meeting {meeting_id}\n\n")
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        next_occurrence = MeetingService.get_next_occurrence(meeting)
        logger.debug(f"\n\nNext occurrence: {next_occurrence}\n\n")
        if next_occurrence:
            serializer = MeetingSerializer(next_occurrence)
            return Response(serializer.data)
        return Response(
            {"message": "No next occurrence found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Move tasks and agenda items to the next occurrence
    @action(detail=True, methods=["POST"])
    def complete(self, request, pk=None):
        meeting = self.get_object()
        MeetingService.complete_meeting(meeting.id)
        return Response(status=status.HTTP_200_OK)

    # Add a MeetingRecurrence to a Meeting
    @action(detail=True, methods=["POST"])
    def add_recurrence(self, request, pk=None):
        logger.debug(f"Request data: {request.data}")
        meeting = self.get_object()
        recurrence_id = request.data.get("recurrence_id")
        logger.debug(f"Recurrence ID: {recurrence_id}")

        if recurrence_id:
            recurrence = get_object_or_404(MeetingRecurrence, pk=recurrence_id)
            meeting.recurrence = recurrence
            meeting.save()

            # Serialize the updated meeting to prepare data for dispatching a task
            serializer = self.get_serializer(meeting)
            logger.debug(
                f"MeetingViewSet.add_recurrence, Serialized data: {serializer.data}"
            )
            # Dispatch the update task to Celery
            self.dispatch_task(serializer.data, create=False)

            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(
                {"message": "Recurrence ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeetingRecurrenceViewSet(AsyncModelViewSet):
    queryset = MeetingRecurrence.objects.all()
    serializer_class = MeetingRecurrenceSerializer


class TaskViewSet(AsyncModelViewSet):
    queryset = Task.objects.select_related(
        "assignee"
    ).all()  # Assuming tasks have an 'assignee'
    serializer_class = TaskSerializer

    # Return all Task objects with related assignee objects
    @action(detail=False, methods=["GET"])
    def list_by_user(self, request):
        user_id = request.query_params.get("user_id")
        tasks = TaskService.get_tasks_by_user(user_id)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.decode())

    # Mark a task as complete
    @action(detail=False, methods=["POST"])
    def mark_complete(self, request):
        TaskService.mark_task_complete(request.data.get("task_id"))
        return Response(status=status.HTTP_200_OK)


class MeetingTaskViewSet(AsyncModelViewSet):
    queryset = MeetingTask.objects.select_related("meeting", "task").all()
    serializer_class = MeetingTaskSerializer

    # Return all MeetingTask objects with related meeting and task objects
    @action(detail=False, methods=["GET"])
    def list_tasks_by_meeting(self, request):
        meeting_id = request.query_params.get("meeting_id")
        meeting_tasks = self.get_queryset().filter(meeting__id=meeting_id)
        serializer = self.get_serializer(meeting_tasks, many=True)
        return Response(serializer.data)


class MeetingAttendeeViewSet(AsyncModelViewSet):
    queryset = MeetingAttendee.objects.select_related("meeting", "user").all()
    serializer_class = MeetingAttendeeSerializer

    # Return all MeetingAttendee objects with related meeting and user objects
    @action(detail=False, methods=["GET"])
    def list_attendees_by_meeting(self, request):
        meeting_id = request.query_params.get("meeting_id")
        attendees = self.get_queryset().filter(meeting__id=meeting_id)
        serializer = self.get_serializer(attendees, many=True)
        return Response(serializer.data)

    # Return all Meeting objects with related MeetingAttendee objects
    @action(detail=False, methods=["GET"])
    def list_meetings_by_user(self, request):
        user_id = request.query_params.get("user_id")
        meetings = MeetingService.get_user_meetings(user_id)
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data)
