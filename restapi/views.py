from django.db import connections
from django.db.models import Q
from django.db.utils import OperationalError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from .services import task_service
from .tasks import *

import logging

logger = logging.getLogger(__name__)


def email_confirm_redirect(request, key):
    return HttpResponseRedirect(f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/")


def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(
        f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
    )


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


# Base viewset class that creates or updates records asynchronously
class AsyncModelViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        logger.debug(f"Performing create for serializer {serializer}")
        if serializer.is_valid(raise_exception=True):
            self.dispatch_task(serializer, create=True)

    def perform_update(self, serializer):
        logger.debug(f"Performing update for serializer {serializer}")
        if serializer.is_valid(raise_exception=True):
            self.dispatch_task(serializer, create=False)

    def dispatch_task(self, serializer, create):
        model_name = self.get_serializer_class().Meta.model.__name__
        data_dict = dict(serializer.data)

        for key in RELATIONS_MODEL_MAPPING:
            if key in data_dict and isinstance(
                data_dict[key], RELATIONS_MODEL_MAPPING[key]
            ):
                logger.debug(f"Found related model {key} in data_dict")
                data_dict[key] = data_dict[key].id

        create_or_update_record.delay(data_dict, model_name, create=create)

    def list_by_meeting(self, request, model):
        meeting_id = request.query_params.get("meeting_id")
        if not meeting_id:
            raise Http404("Meeting ID is required")

        meeting = get_object_or_404(Meeting, pk=meeting_id)
        queryset = model.objects.filter(meeting=meeting)
        serializer = self.get_serializer_for_model(model, queryset, many=True)
        return Response(serializer.data)

    def get_serializer_for_model(self, model, *args, **kwargs):
        serializer_class = MODEL_SERIALIZER_MAPPING.get(model)
        if serializer_class is None:
            raise ValueError("No serializer found for the provided model")
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class UserViewSet(AsyncModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


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
        serializer = MeetingRecurrenceSerializer(recurrence)
        return Response(serializer.data)

    # Returns a serialized Meeting object
    @action(detail=False, methods=["GET"])
    def get_next_occurrence(self, request):
        meeting_id = request.query_params.get("meeting_id")
        meeting = Meeting.objects.get(pk=meeting_id)
        next_meeting = meeting.get_next_occurrence()

        if next_meeting is None:
            return Response(
                {"message": "Next occurrence is being scheduled"},
                status=status.HTTP_202_ACCEPTED,
            )

        serializer = MeetingSerializer(next_meeting)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_recurrence(self, request, pk=None):
        meeting = self.get_object()
        recurrence_data = request.data.get("recurrence")

        # Validate the recurrence data
        recurrence_serializer = MeetingRecurrenceSerializer(data=recurrence_data)
        if recurrence_serializer.is_valid():
            recurrence = recurrence_serializer.save()

            # Associate the recurrence with the meeting
            meeting.recurrence = recurrence
            meeting.save(update_fields=["recurrence"])

            return Response({"status": "recurrence set"}, status=status.HTTP_200_OK)
        else:
            return Response(
                recurrence_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

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


class UserPreferencesViewSet(AsyncModelViewSet):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer


class EventTimeViewSet(AsyncModelViewSet):
    queryset = EventTime.objects.all()
    serializer_class = EventTimeSerializer


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/"
    client_class = OAuth2Client
