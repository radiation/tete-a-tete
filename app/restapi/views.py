from django.shortcuts import render
from django.db.models import Q
from rest_framework import generics
from .models import *
from .serializers import *

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserFlatSerializer

class UserListByIDView(generics.ListCreateAPIView):
    def get_queryset(self):
        id_value = self.kwargs.get('id_value')
        return User.objects.filter(id=id_value)
    serializer_class = UserFlatSerializer

class MeetingCreateView(generics.CreateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingFlatSerializer

class MeetingListView(generics.ListAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingNestedSerializer

class MeetingListByIDView(generics.ListAPIView):
    def get_queryset(self):
        id_value = self.kwargs.get('id_value')
        return Meeting.objects.filter(id=id_value)
    serializer_class = MeetingNestedSerializer

class MeetingListByUserView(generics.ListAPIView):
    def get_queryset(self):
        user_id_value=self.kwargs.get('user_id_value')
        return Meeting.objects.filter(Q(scheduler__id=user_id_value) | Q(attendee__id=user_id_value)).order_by('start_date')
    serializer_class = MeetingNestedSerializer

class ActionItemListView(generics.ListCreateAPIView):
    queryset = ActionItem.objects.all()
    serializer_class = ActionItemNestedSerializer

class ActionItemCreateView(generics.ListCreateAPIView):
    queryset = ActionItem.objects.all()
    serializer_class = ActionItemFlatSerializer

class ActionItemListByIDView(generics.ListAPIView):
    def get_queryset(self):
        id_value = self.kwargs.get('id_value')
        return ActionItem.objects.filter(id=id_value)
    serializer_class = ActionItemNestedSerializer

class ActionItemListByUserView(generics.ListAPIView):
    def get_queryset(self):
        user_id_value=self.kwargs.get('user_id_value')
        return ActionItem.objects.filter(Q(assignee__id=user_id_value))
    serializer_class = ActionItemNestedSerializer

class ActionItemListByMeetingView(generics.ListAPIView):
    def get_queryset(self):
        meeting_id_value=self.kwargs.get('meeting_id_value')
        return ActionItem.objects.filter(Q(assignee__id=meeting_id_value))
    serializer_class = ActionItemNestedSerializer

class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionFlatSerializer

class QuestionCreateView(generics.CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionFlatSerializer

class QuestionListByIDView(generics.ListAPIView):
    def get_queryset(self):
        id_value = self.kwargs.get('id_value')
        return Question.objects.filter(id=id_value)
    serializer_class = QuestionFlatSerializer

class QuestionAnswerListView(generics.ListAPIView):
    queryset = QuestionAnswer.objects.all()
    serializer_class = QuestionAnswerNestedSerializer

class QuestionAnswerCreateView(generics.CreateAPIView):
    queryset = QuestionAnswer.objects.all()
    serializer_class = QuestionAnswerFlatSerializer

class QuestionAnswerListByIDView(generics.ListAPIView):
    def get_queryset(self):
        id_value = self.kwargs.get('id_value')
        return QuestionAnswer.objects.filter(id=id_value)
    serializer_class = QuestionAnswerNestedSerializer