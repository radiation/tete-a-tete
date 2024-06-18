import datetime
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from users.models import CustomUser
from restapi.models import Meeting, Task, MeetingAttendee, MeetingTask
from restapi.serializers import (
    TaskSerializer,
    MeetingAttendeeSerializer,
    MeetingTaskSerializer,
)
from common.tasks import create_or_update_record
import json
import logging

logger = logging.getLogger(__name__)

# These generic mappings are used to pull model objects from IDs and vice versa
RELATIONS_MODEL_MAPPING = {
    "assignee": CustomUser,
    "meeting": Meeting,
    "task": Task,
    "user": CustomUser,
}

# This mapping is used to get the appropriate serializer for a given model
MODEL_SERIALIZER_MAPPING = {
    Task: TaskSerializer,
    MeetingAttendee: MeetingAttendeeSerializer,
    MeetingTask: MeetingTaskSerializer,
}


"""
We're extending ModelViewSet to handle asynchronous record creation and updates.
"""


class AsyncModelViewSet(viewsets.ModelViewSet):

    # Overload ModelViewSet.create to dispatch a task via celery
    def perform_create(self, serializer):
        logger.debug(f"Performing create for data {serializer.validated_data}")
        self.dispatch_task(serializer.validated_data, create=True)

    # Overload ModelViewSet.update to dispatch a task via celery
    def perform_update(self, serializer):
        logger.debug(f"Performing update for data {serializer.validated_data}")
        self.dispatch_task(serializer.validated_data, create=False)

    # Dispatch a celery task to create or update a record
    def dispatch_task(self, data, create):
        model_name = self.get_serializer_class().Meta.model.__name__
        logger.debug(f"Dispatching task for {model_name} with data: {data}")
        prepared_data = self.prepare_data_for_task(data)

        logger.debug(f"Dispatching task for {model_name} with data: {prepared_data}")
        create_or_update_record.delay(prepared_data, model_name, create=create)

    # Prepare the data by converting related models to their IDs
    def prepare_data_for_task(self, data):
        logger.debug(f"\n\nOriginal data: {data}\n\n")
        prepared_data = {}
        for field_name, value in data.items():
            if isinstance(value, models.Model):
                # Convert model instance to ID
                prepared_data[field_name] = value.id
            elif isinstance(value, (list, models.QuerySet)):
                # Convert list of model instances to list of IDs
                prepared_data[field_name] = [item.id for item in value]
            elif isinstance(value, (datetime.date, datetime.datetime)):
                # Format datetime objects as string
                prepared_data[field_name] = value.isoformat()
            else:
                prepared_data[field_name] = value

        try:
            json.dumps(prepared_data)  # Test if data is serializable
        except TypeError as e:
            logger.error(f"Data serialization error: {e}")
            raise

        logger.debug(f"\n\nPrepared data: {prepared_data}\n\n")
        return prepared_data


    # This could be attendees, tasks, etc, so we pass the model as a param
    def list_by_meeting(self, request, model):
        meeting_id = request.query_params.get("meeting_id")

        # The request must include a meeting_id parameter
        if not meeting_id:
            raise Http404("Meeting ID is required")

        meeting = get_object_or_404(Meeting, pk=meeting_id)
        queryset = model.objects.filter(meeting=meeting)
        serializer = self.get_serializer_for_model(model, queryset, many=True)
        return Response(serializer.data)

    # We need to map the serializer to the model so we can use it to get serialized data
    def get_serializer_for_model(self, model, *args, **kwargs):
        serializer_class = MODEL_SERIALIZER_MAPPING.get(model)
        if serializer_class is None:
            raise ValueError("No serializer found for the provided model")
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)
