from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from .models import *

class UserFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class MeetingFlatSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'

class MeetingNestedSerializer(WritableNestedModelSerializer):
    scheduler = UserFlatSerializer()
    attendee = UserFlatSerializer()
    class Meta:
        model = Meeting
        fields = '__all__'

class ActionItemFlatSerializer(WritableNestedModelSerializer):
    class Meta:
        model = ActionItem
        fields = '__all__'

class ActionItemNestedSerializer(WritableNestedModelSerializer):
    meeting = MeetingNestedSerializer()
    class Meta:
        model = ActionItem
        fields = '__all__'

class QuestionFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class QuestionAnswerFlatSerializer(WritableNestedModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = '__all__'

class QuestionAnswerNestedSerializer(WritableNestedModelSerializer):
    question = QuestionFlatSerializer()
    asker = UserFlatSerializer()
    answerer = UserFlatSerializer()
    class Meta:
        model = QuestionAnswer
        fields = '__all__'

class AgendaItemFlatSerializer(WritableNestedModelSerializer):
    class Meta:
        model = AgendaItem
        fields = '__all__'

class AgendaItemNestedSerializer(WritableNestedModelSerializer):
    meeting = MeetingNestedSerializer()
    class Meta:
        model = AgendaItem
        fields = '__all__'