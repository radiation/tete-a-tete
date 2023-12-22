from django.db.models import Q
from django.http import HttpResponseRedirect
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from .tasks import *
import logging

logger = logging.getLogger(__name__)


def email_confirm_redirect(request, key):
    return HttpResponseRedirect(f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/")

def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/")

'''
Base viewset class that automatically creates or updates records asynchronously
'''
class AsyncModelViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        if serializer.is_valid():
            model_name = self.get_serializer_class().Meta.model.__name__
            data = serializer.validated_data

            # Log the validated data
            print(f"Validated data before conversion: {data}")

            # Convert to a regular dictionary
            data_dict = dict(data)

            # Log the converted data
            print(f"Data dict after conversion: {data_dict}")

            # Check and replace foreign key field
            if 'assignee' in data_dict:
                # Ensure we are dealing with a CustomUser instance
                if isinstance(data_dict['assignee'], CustomUser):
                    data_dict['assignee'] = data_dict['assignee'].id
                    print(f"Assignee ID: {data_dict['assignee']}")
                else:
                    print(f"Assignee is not a CustomUser instance: {data_dict['assignee']}")

            # Send this dictionary to the Celery task
            create_or_update_record.delay(data_dict, model_name, create=True)

    def perform_update(self, serializer):

        if serializer.is_valid():
            model_name = self.get_serializer_class().Meta.model.__name__
            create_or_update_record.delay(serializer.validated_data, model_name, create=False)

class UserViewSet(AsyncModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class MeetingViewSet(AsyncModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

class TaskViewSet(AsyncModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=['GET'])
    def list_by_user(self, request):
        user_id = request.query_params.get('user_id')
        queryset = Task.objects.filter(Q(assignee__id=user_id))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def mark_complete(self, request):
        action_item_id = request.data.get('action_item_id')
        action_item = Task.objects.get(pk=action_item_id)
        action_item.completed = True
        action_item.save()
        return Response(status=status.HTTP_200_OK)

class MeetingTaskViewSet(AsyncModelViewSet):
    queryset = MeetingTask.objects.all()
    serializer_class = MeetingTaskSerializer

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=['GET'])
    def list_by_meeting(self, request):
        meeting_id = request.query_params.get('meeting_id')
        queryset = Task.objects.filter(Q(meeting__id=meeting_id))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class MeetingAttendeeViewSet(AsyncModelViewSet):
    queryset = MeetingAttendee.objects.all()
    serializer_class = MeetingAttendeeSerializer

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=['GET'])
    def list_by_meeting(self, request):
        meeting_id = request.query_params.get('meeting_id')
        queryset = Task.objects.filter(Q(meeting__id=meeting_id))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def list_by_user(self, request):
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