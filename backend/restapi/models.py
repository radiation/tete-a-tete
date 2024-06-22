from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from common.constants import WEEKDAY_CHOICES, MONTH_WEEK_CHOICES, FREQUENCY_CHOICES

import logging

logger = logging.getLogger(__name__)


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

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            logger.warn(
                f"{str(self)}: End date {str(self.end_date)} "
                f"must be after start date {str(self.start_date)}"
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

    def __str__(self) -> str:
        return (
            f"{self.frequency.capitalize()} recurrence "
            f"starting {self.created_at.strftime('%Y-%m-%d')}"
        )


class MeetingAttendee(models.Model):
    meeting = models.ForeignKey("Meeting", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True
    )
    is_scheduler = models.BooleanField(default=False)

    class Meta:
        unique_together = (("meeting", "user"),)


class MeetingTask(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    task = models.ForeignKey("Task", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("meeting", "task"),)


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

        # Check if the task is marked as not completed
        # and clear the completed_date if so
        if not self.completed:
            self.completed_date = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.assignee}: {self.title}"
