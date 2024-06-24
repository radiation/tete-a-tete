import factory
from factory.django import DjangoModelFactory
from meetings.models import MeetingTask


class MeetingTaskFactory(DjangoModelFactory):
    class Meta:
        model = MeetingTask

    meeting = factory.SubFactory("meetings.factories.MeetingFactory")
    task = factory.SubFactory("meetings.factories.TaskFactory")
