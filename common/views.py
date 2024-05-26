from django.db import connections
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import CustomUser
from restapi.models import Meeting, Task, MeetingAttendee
from restapi.serializers import TaskSerializer, MeetingAttendeeSerializer
from restapi.tasks import create_or_update_record

import logging

logger = logging.getLogger(__name__)

# For looking up related models
RELATIONS_MODEL_MAPPING = {
    "assignee": CustomUser,
    "meeting": Meeting,
    "task": Task,
    "user": CustomUser,
}

MODEL_SERIALIZER_MAPPING = {
    Task: TaskSerializer,
    MeetingAttendee: MeetingAttendeeSerializer,
}

# Base viewset class that creates or updates records asynchronously
class AsyncModelViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        logger.debug(f"Performing create for serializer {serializer}")
        if serializer.is_valid(raise_exception=True):
            self.dispatch_task(serializer, create=True)

    def perform_update(self, serializer):
        logger.debug(f"Performing update for serializer {serializer}")
        if serializer.is_valid(raise_exception=True):
            self.dispatch_task(serializer, create=False)

    def dispatch_task(self, serializer, create):
        model_name = self.get_serializer_class().Meta.model.__name__
        data_dict = dict(serializer.data)

        for key in RELATIONS_MODEL_MAPPING:
            if key in data_dict and isinstance(
                data_dict[key], RELATIONS_MODEL_MAPPING[key]
            ):
                logger.debug(f"Found related model {key} in data_dict")
                data_dict[key] = data_dict[key].id

        create_or_update_record.delay(data_dict, model_name, create=create)

    def list_by_meeting(self, request, model):
        meeting_id = request.query_params.get("meeting_id")
        if not meeting_id:
            raise Http404("Meeting ID is required")

        meeting = get_object_or_404(Meeting, pk=meeting_id)
        queryset = model.objects.filter(meeting=meeting)
        serializer = self.get_serializer_for_model(model, queryset, many=True)
        return Response(serializer.data)

    def get_serializer_for_model(self, model, *args, **kwargs):
        serializer_class = MODEL_SERIALIZER_MAPPING.get(model)
        if serializer_class is None:
            raise ValueError("No serializer found for the provided model")
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)
