import factory
from factory.django import DjangoModelFactory

from restapi.models import MeetingAttendee


class MeetingAttendeeFactory(DjangoModelFactory):
    class Meta:
        model = MeetingAttendee

    meeting = factory.SubFactory("restapi.factories.MeetingFactory")
    user = factory.SubFactory("users.factories.CustomUserFactory")
