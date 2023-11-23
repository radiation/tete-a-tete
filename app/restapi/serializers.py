from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class MeetingFlatSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'

class MeetingNestedSerializer(WritableNestedModelSerializer):
    scheduler = UserSerializer()
    attendee = UserSerializer()
    class Meta:
        model = Meeting
        fields = '__all__'

class ActionItemSerializer(WritableNestedModelSerializer):
    meeting = MeetingSerializer()
    class Meta:
        model = ActionItem
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class QuestionAnswerSerializer(WritableNestedModelSerializer):
    question = QuestionSerializer()
    asker = UserSerializer()
    answerer = UserSerializer()
    class Meta:
        model = QuestionAnswer
        fields = '__all__'