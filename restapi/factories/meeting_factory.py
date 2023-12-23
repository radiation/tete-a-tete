import factory
import datetime
from factory.django import DjangoModelFactory

from restapi.models import Meeting

class MeetingFactory(DjangoModelFactory):
    class Meta:
        model = Meeting

    title = factory.Faker('sentence')
    start_date = factory.Faker('date_time')
    end_date = factory.LazyAttribute(lambda o: o.start_date + datetime.timedelta(minutes=30))
    notes = factory.Faker('sentence')