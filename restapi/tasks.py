from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from users.services import UserService
from users.serializers import (
    UserSerializer,
    UserPreferencesSerializer,
)
from restapi.serializers import *

import logging

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
