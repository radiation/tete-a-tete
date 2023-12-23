from factory.django import DjangoModelFactory
from django.utils import timezone
from restapi.models import Task

import factory

class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph', nb_sentences=3)
    due_date = factory.Faker('future_datetime', tzinfo=timezone.get_current_timezone())
    completed = False
    completed_date = None
    assignee = factory.SubFactory('restapi.factories.CustomUserFactory')