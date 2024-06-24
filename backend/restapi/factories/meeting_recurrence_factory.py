import random

import factory
from factory.fuzzy import FuzzyInteger
from restapi.models import (
    FREQUENCY_CHOICES,
    MONTH_WEEK_CHOICES,
    WEEKDAY_CHOICES,
    MeetingRecurrence,
)


class MeetingRecurrenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MeetingRecurrence

    frequency = factory.LazyFunction(lambda: random.choice(FREQUENCY_CHOICES)[0])
    week_day = factory.LazyFunction(lambda: random.choice(WEEKDAY_CHOICES)[0])
    month_week = factory.LazyFunction(lambda: random.choice(MONTH_WEEK_CHOICES)[0])
    interval = FuzzyInteger(1, 4)
