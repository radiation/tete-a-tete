from django.db import models
from common.constants import WEEKDAY_CHOICES


class EventTime(models.Model):
    day = models.IntegerField(choices=WEEKDAY_CHOICES)
    time = models.TimeField()

    class Meta:
        unique_together = [["day", "time"]]
        ordering = [["day", "time"]]
