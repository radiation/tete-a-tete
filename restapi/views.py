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

def email_confirm_redirect(request, key):
    return HttpResponseRedirect(f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/")

def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/")

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()

    def get_serializer_class(self):
        if self.action in ('create','update'):
            return MeetingFlatSerializer
        return MeetingNestedSerializer

    def perform_create(self, serializer):
        scheduler = CustomUser.objects.get(pk=self.request.data.get('scheduler'))
        attendee = CustomUser.objects.get(pk=self.request.data.get('attendee'))
        serializer.save(scheduler=scheduler, attendee=attendee)

    @action(detail=False, methods=['GET'])
    def list_by_user(self, request):
        user_id = request.query_params.get('user_id')
        queryset = Meeting.objects.filter(
            Q(scheduler__id=user_id) | Q(attendee__id=user_id)
        ).order_by('start_date')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ActionItemViewSet(viewsets.ModelViewSet):
    queryset = ActionItem.objects.all()

    def get_serializer_class(self):
        if self.action in ('create','update'):
            return AgendaItemFlatSerializer
        return AgendaItemNestedSerializer

    @action(detail=False, methods=['GET'])
    def list_by_user(self, request):
        user_id = request.query_params.get('user_id')
        queryset = ActionItem.objects.filter(Q(assignee__id=user_id))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def list_by_meeting(self, request):
        meeting_id = request.query_params.get('meeting_id')
        queryset = ActionItem.objects.filter(Q(meeting__id=meeting_id))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def mark_complete(self, request):
        action_item_id = request.data.get('action_item_id')
        action_item = ActionItem.objects.get(pk=action_item_id)
        action_item.completed = True
        action_item.save()
        return Response(status=status.HTTP_200_OK)
    
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionAnswerViewSet(viewsets.ModelViewSet):
    queryset = QuestionAnswer.objects.all()

    def get_serializer_class(self):
        if self.action in ('create','update'):
            return MeetingFlatSerializer
        return MeetingNestedSerializer

class AgendaItemViewSet(viewsets.ModelViewSet):
    queryset = AgendaItem.objects.all()
    serializer_class = AgendaItemNestedSerializer

    @action(detail=False, methods=['GET'])
    def list_by_meeting(self, request):
        meeting_id = request.query_params.get('meeting_id')
        queryset = AgendaItem.objects.filter(Q(meeting__id=meeting_id))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def mark_complete(self, request):
        agenda_item_id = request.data.get('agenda_item_id')
        agenda_item = AgendaItem.objects.get(pk=agenda_item_id)
        agenda_item.completed = True
        agenda_item.save()
        return Response(status=status.HTTP_200_OK)
    
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/"
    client_class = OAuth2Client