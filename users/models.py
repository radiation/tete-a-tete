from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.constants import WEEKDAY_CHOICES
from common.models import EventTime
from .managers import CustomUserManager

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


class UserDigest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    send_time = models.ForeignKey(EventTime, on_delete=models.CASCADE)
