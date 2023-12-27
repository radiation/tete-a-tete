from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from enum import IntEnum

from .managers import CustomUserManager

import logging

logger = logging.getLogger(__name__)

class DaysOfWeek(IntEnum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=30, null= True, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, null= True, blank=True)
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
            logger.exception(f'IntegrityError while saving CustomUser: {e}', exc_info=False)

class UserPreferences(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    timezone = models.CharField(max_length=50, default="UTC")
    working_days = models.IntegerField(models.IntegerField(choices=[(tag, tag.value) for tag in DaysOfWeek]))
    working_hours_start = models.TimeField(default="09:00:00")
    working_hours_end = models.TimeField(default="17:00:00")

class EventTime(models.Model):
    day = models.IntegerField(choices=[(tag, tag.value) for tag in DaysOfWeek])
    time = models.TimeField()

    unique_together = [["day", "time"]]

class UserDigest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    send_time = models.ForeignKey(EventTime, on_delete=models.CASCADE)

class Task(models.Model):
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
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
        return f'{self.assignee}: {self.title}'
    
class Meeting(models.Model):    
    title = models.CharField(default="", max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    notes = models.TextField(default="")
    num_reschedules = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        # Check that end_date is after start_date
        if self.end_date and self.start_date and self.end_date < self.start_date:
            logger.info(f"{str(self)}: End date {str(self.end_date)} must be after start date {str(self.start_date)}")
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
        return f'{self.title}'

class MeetingAttendee(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    is_scheduler = models.BooleanField(default=False)

    unique_together = [["meeting", "user"]]

class MeetingTask(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    unique_together = [["meeting", "task"]]

