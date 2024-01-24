from celery import Celery, shared_task
from celery.schedules import crontab
from django import test
from django.apps import apps
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from restapi.consumers import notify_channel_layer

from .serializers import *
from .services.user_service import UserService

import logging
from celery.signals import task_postrun

logger = logging.getLogger(__name__)

serializers_dict = {
    "User": UserSerializer,
    "UserPreferences": UserPreferencesSerializer,
    "EventTime": EventTimeSerializer,
    "Meeting": MeetingSerializer,
    "MeetingRecurrence": MeetingRecurrenceSerializer,
    "Task": TaskSerializer,
    "MeetingTask": MeetingTaskSerializer,
    "MeetingAttendee": MeetingAttendeeSerializer,
}

app = Celery()


@shared_task
def send_email_to_user(subject, message, from_email, user_email):
    send_mail(subject, message, from_email, [user_email])


@shared_task
def send_meeting_reminders():
    time_threshold = timezone.now() + timedelta(hours=24)
    upcoming_meetings = Meeting.objects.filter(
        start_date__lte=time_threshold
    ).prefetch_related("meetingattendee_set__user")
    logger.debug(f"Found {len(upcoming_meetings)} meetings to send reminders for.")

    for meeting in upcoming_meetings:
        logger.debug(f"Sending reminders for meeting {meeting.id}")
        for attendee in meeting.meetingattendee_set.all():
            user = attendee.user
            logger.debug(f"Sending reminder to user {user.email}")

            user_service = UserService(user)
            user_service.send_email(
                subject="Meeting Reminder",
                message=f"Reminder: You have a meeting titled '{meeting.title}' scheduled at {meeting.start_date}.",
                from_email="noreply@example.com",
            )

        meeting.reminders_sent = True
        meeting.save()


@shared_task(name="high_priority:create_or_update_record")
def create_or_update_record(validated_data, model_name, create=True):
    logger.debug(
        f"Creating/Updating record for model {model_name} with data: {validated_data}"
    )
    Model = apps.get_model("restapi", model_name)
    SerializerClass = serializers_dict[model_name]

    print(f"Create: {create}")
    print(f"Model: {Model}")
    print(f"Serializer: {SerializerClass}")
    print(f"Data: {validated_data}")

    if create:
        serializer = SerializerClass(data=validated_data)
    else:
        instance = Model.objects.get(pk=validated_data["id"])
        serializer = SerializerClass(instance, data=validated_data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        print(f"Serializer errors: {serializer.errors}")
        logger.error(f"Serializer errors: {serializer.errors}")
        return serializer.errors


@shared_task(name="high_priority:create_or_update_batch")
def create_or_update_batch(tasks_data, model_name):
    Model = apps.get_model("restapi", model_name)
    SerializerClass = serializers_dict[model_name]

    for data in tasks_data:
        instance = Model.objects.get(pk=data["id"])
        serializer = SerializerClass(instance, data=data)

        if serializer.is_valid():
            serializer.save()
        else:
            logger.error(
                f"Serializer errors for {model_name} ID {data['id']}: {serializer.errors}"
            )

    return "Batch update completed"


@shared_task()
def task_test_logger():
    logger.info("test")


@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    notify_channel_layer(task_id)
