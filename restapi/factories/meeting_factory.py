import factory
import datetime
from django.utils import timezone
from factory.django import DjangoModelFactory

from restapi.models import Meeting


class MeetingFactory(DjangoModelFactory):
    class Meta:
        model = Meeting

    recurrence = factory.SubFactory("restapi.factories.MeetingRecurrenceFactory")
    title = factory.Faker("sentence")
    start_date = factory.Faker(
        "future_datetime", tzinfo=timezone.get_current_timezone()
    )
    end_date = factory.LazyAttribute(
        lambda o: o.start_date + datetime.timedelta(minutes=30)
    )
    notes = factory.Faker("sentence")
