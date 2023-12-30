from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
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
    return HttpResponseRedirect(f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/")

#For looking up related models
relations_dict = {
    'assignee': CustomUser,
    'meeting': Meeting,
    'task': Task,
    'user': CustomUser,
}

MODEL_SERIALIZER_MAPPING = {
    Task: TaskSerializer,
    MeetingAttendee: MeetingAttendeeSerializer,
}

#Base viewset class that automatically creates or updates records asynchronously
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
        data_dict = dict(serializer.validated_data)

        for key in relations_dict:
            if key in data_dict and isinstance(data_dict[key], relations_dict[key]):
                logger.debug(f"Found related model {key} in data_dict")
                data_dict[key] = data_dict[key].id

        create_or_update_record.delay(data_dict, model_name, create=create)

    def list_by_meeting(self, request, model):
        meeting_id = request.query_params.get('meeting_id')
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
        kwargs['context'] = self.get_serializer_context()
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
    @action(detail=False, methods=['GET'])
    def get_meeting_recurrence(self, request):
        meeting_id = request.query_params.get('meeting_id')
        recurrence = MeetingRecurrence.objects.get(meeting__id=meeting_id)
        return Response(recurrence)

    # Returns a Meeting object  
    @action(detail=False, methods=['GET'])
    def get_next_occurrence(self, request):
        meeting_id = request.query_params.get('meeting_id')
        meeting = Meeting.objects.get(pk=meeting_id)
        next_occurrence = meeting.get_next_occurrence()
        return Response(next_occurrence)

    # Move tasks and agenda items to the next occurrence
    @action(detail=False, methods=['POST'])
    def complete(self, request):
        meeting_service.complete_meeting(request.data.get('meeting_id'))
        return Response(status=status.HTTP_200_OK)

class MeetingRecurrenceViewSet(AsyncModelViewSet):
    queryset = MeetingRecurrence.objects.all()
    serializer_class = MeetingRecurrenceSerializer

class TaskViewSet(AsyncModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=['GET'])
    def list_by_user(self, request):
        user_id = request.query_params.get('user_id')
        tasks = Task.objects.filter(assignee__id=user_id)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def mark_complete(self, request):
        task_service.mark_task_complete(request.data.get('task_id'))
        return Response(status=status.HTTP_200_OK)

class MeetingTaskViewSet(AsyncModelViewSet):
    queryset = MeetingTask.objects.all()
    serializer_class = MeetingTaskSerializer

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=['GET'])
    def list_tasks_by_meeting(self, request):
        return self.list_by_meeting(request, Task)

class MeetingAttendeeViewSet(AsyncModelViewSet):
    queryset = MeetingAttendee.objects.all()
    serializer_class = MeetingAttendeeSerializer

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=['GET'])
    def list_attendees_by_meeting(self, request):
        return self.list_by_meeting(request, Task)

    @action(detail=False, methods=['GET'])
    def list_meetings_by_user(self, request):
        user_id = request.query_params.get('user_id')
        queryset = Meeting.objects.filter(
            Q(scheduler__id=user_id) | Q(attendee__id=user_id)
        ).order_by('start_date')
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
