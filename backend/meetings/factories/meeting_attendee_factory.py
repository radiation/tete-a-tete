import factory
from factory.django import DjangoModelFactory
from meetings.models import MeetingAttendee


class MeetingAttendeeFactory(DjangoModelFactory):
    class Meta:
        model = MeetingAttendee

    meeting = factory.SubFactory("meetings.factories.MeetingFactory")
    user = factory.SubFactory("users.factories.CustomUserFactory")
