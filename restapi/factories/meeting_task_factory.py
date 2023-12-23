from factory.django import DjangoModelFactory

import factory

from restapi.models import MeetingTask

class MeetingTaskFactory(DjangoModelFactory):
    class Meta:
        model = MeetingTask

    meeting = factory.SubFactory('restapi.factories.MeetingFactory')
    task = factory.SubFactory('restapi.factories.TaskFactory')