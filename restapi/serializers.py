from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class UserPreferencesSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = UserPreferences
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['user'] = UserSerializer(read_only=True)
        return super(UserPreferencesSerializer, self).to_representation(instance)

class EventTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTime
        fields = '__all__'

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Task
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['assignee'] = UserSerializer(read_only=True)
        return super(TaskSerializer, self).to_representation(instance)

class MeetingTaskSerializer(serializers.ModelSerializer):
    meeting = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.all())
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    class Meta:
        model = MeetingTask
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['meeting'] = MeetingSerializer(read_only=True)
        self.fields['task'] = TaskSerializer(read_only=True)
        return super(MeetingTaskSerializer, self).to_representation(instance)

class MeetingAttendeeSerializer(serializers.ModelSerializer):
    meeting = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = MeetingAttendee
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['meeting'] = MeetingSerializer(read_only=True)
        self.fields['user'] = UserSerializer(read_only=True)
        return super(MeetingAttendeeSerializer, self).to_representation(instance)

class UserDigestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    send_time = serializers.PrimaryKeyRelatedField(queryset=EventTime.objects.all())
    class Meta:
        model = UserDigest
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['user'] = UserSerializer(read_only=True)
        self.fields['send_time'] = EventTimeSerializer(read_only=True)
        return super(UserDigestSerializer, self).to_representation(instance)