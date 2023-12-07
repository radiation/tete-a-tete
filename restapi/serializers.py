from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from .models import *
'''    scheduler = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    attendee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
'''
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class MeetingFlatSerializer(WritableNestedModelSerializer):
    scheduler = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    attendee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Meeting
        fields = '__all__'

class MeetingNestedSerializer(WritableNestedModelSerializer):
    scheduler = UserSerializer()
    attendee = UserSerializer()
    class Meta:
        model = Meeting
        fields = '__all__'

class ActionItemFlatSerializer(WritableNestedModelSerializer):
    meeting = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.all())
    class Meta:
        model = ActionItem
        fields = '__all__'

class ActionItemNestedSerializer(WritableNestedModelSerializer):
    meeting = MeetingNestedSerializer()
    class Meta:
        model = ActionItem
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class QuestionAnswerFlatSerializer(WritableNestedModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    asker = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    answerer = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = QuestionAnswer
        fields = '__all__'

class QuestionAnswerNestedSerializer(WritableNestedModelSerializer):
    question = QuestionSerializer()
    asker = UserSerializer()
    answerer = UserSerializer()
    class Meta:
        model = QuestionAnswer
        fields = '__all__'

class AgendaItemFlatSerializer(WritableNestedModelSerializer):
    meeting = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.all())
    class Meta:
        model = AgendaItem
        fields = '__all__'

class AgendaItemNestedSerializer(WritableNestedModelSerializer):
    meeting = MeetingNestedSerializer()
    class Meta:
        model = AgendaItem
        fields = '__all__'