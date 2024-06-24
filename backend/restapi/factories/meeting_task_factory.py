import factory
from factory.django import DjangoModelFactory
from restapi.models import MeetingTask


class MeetingTaskFactory(DjangoModelFactory):
    class Meta:
        model = MeetingTask

    meeting = factory.SubFactory("restapi.factories.MeetingFactory")
    task = factory.SubFactory("restapi.factories.TaskFactory")
