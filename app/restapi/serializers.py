from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class MeetingSerializer(serializers.ModelSerializer):
    scheduler = UserSerializer()
    attendee = UserSerializer()
    class Meta:
        model = Meeting
        fields = '__all__'

class ActionItemSerializer(serializers.ModelSerializer):
    meeting = MeetingSerializer()
    class Meta:
        model = ActionItem
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class QuestionAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    asker = UserSerializer()
    answerer = UserSerializer()
    class Meta:
        model = QuestionAnswer
        fields = '__all__'