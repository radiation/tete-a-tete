from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .utils import WEEKDAY_CHOICES, MONTH_WEEK_CHOICES, FREQUENCY_CHOICES
from .managers import CustomUserManager
from .services import meeting_service

import logging

logger = logging.getLogger(__name__)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=30, null=True, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError as e:
            logger.exception(
                f"IntegrityError while saving CustomUser: {e}", exc_info=False
            )


class UserPreferences(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True
    )
    timezone = models.CharField(max_length=50, default="UTC")
    working_days = models.IntegerField(
        models.IntegerField(choices=WEEKDAY_CHOICES, null=True, blank=True)
    )
    working_hours_start = models.TimeField(default="09:00:00")
    working_hours_end = models.TimeField(default="17:00:00")


class EventTime(models.Model):
    day = models.IntegerField(choices=WEEKDAY_CHOICES)
    time = models.TimeField()

    class Meta:
        unique_together = [["day", "time"]]
        ordering = [["day", "time"]]


class UserDigest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    send_time = models.ForeignKey(EventTime, on_delete=models.CASCADE)


class Meeting(models.Model):
    recurrence = models.ForeignKey(
        "MeetingRecurrence", null=True, blank=True, on_delete=models.CASCADE
    )
    title = models.CharField(default="", max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    duration = models.IntegerField(default=30)
    notes = models.TextField(default="")
    num_reschedules = models.IntegerField(default=0)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def get_next_occurrence(self):
        next_meeting = (
            Meeting.objects.filter(
                recurrence=self.recurrence, start_date__gt=self.start_date
            )
            .order_by("start_date")
            .first()
        )

        if next_meeting:
            return next_meeting
        elif self.recurrence:
            meeting_service.create_next_meeting(self)
            return None

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            logger.warn(
                f"{str(self)}: End date {str(self.end_date)} must be after start date {str(self.start_date)}"
            )
            raise ValidationError("End date must be after start date")

        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        if self.pk is None:
            logger.debug(f"Creating new meeting: {self.title}")
        else:
            logger.debug(f"Updating meeting {self.pk}: {self.title}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.start_date}: {self.title}"


class MeetingRecurrence(models.Model):
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    week_day = models.IntegerField(choices=WEEKDAY_CHOICES, null=True, blank=True)
    month_week = models.IntegerField(choices=MONTH_WEEK_CHOICES, null=True, blank=True)
    interval = models.IntegerField(
        default=1
    )  # Used for daily, weekly, and monthly frequencies
    end_recurrence = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def get_next_occurrence(self, source_datetime):
        return meeting_service.get_next_occurrence_date(self, source_datetime)


class MeetingAttendee(models.Model):
    meeting = models.ForeignKey("Meeting", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True
    )
    is_scheduler = models.BooleanField(default=False)

    unique_together = [["meeting", "user"]]


class MeetingTask(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    task = models.ForeignKey("Task", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [["meeting", "task"]]


class Task(models.Model):
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True
    )
    title = models.CharField(default="", max_length=100)
    description = models.CharField(default="", max_length=1000)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.pk is None:
            logger.debug(f"Creating new task: {str(self)}")
        else:
            logger.debug(f"Updating task {str(self)}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.assignee}: {self.title}"
