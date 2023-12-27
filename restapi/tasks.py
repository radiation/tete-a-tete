from celery import Celery, shared_task
from celery.schedules import crontab
from django import test
from django.apps import apps

from .serializers import *

import logging

logger = logging.getLogger(__name__)

serializers_dict = {
    'User': UserSerializer,
    'UserPreferences': UserPreferencesSerializer,
    'EventTime': EventTimeSerializer,
    'Meeting': MeetingSerializer,
    'Task': TaskSerializer,
    'MeetingTask': MeetingTaskSerializer,
    'MeetingAttendee': MeetingAttendeeSerializer,
}

app = Celery()

@shared_task
def create_or_update_record(validated_data, model_name, create=True):
    logger.debug(f"Creating/Updating record for model {model_name} with data: {validated_data}")

    Model = apps.get_model('restapi', model_name)
    SerializerClass = serializers_dict[model_name]

    if create:
        serializer = SerializerClass(data=validated_data)
    else:
        instance = Model.objects.get(pk=validated_data['id'])
        serializer = SerializerClass(instance, data=validated_data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        logger.error(f"Serializer errors: {serializer.errors}")
        return serializer.errors
