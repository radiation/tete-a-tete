from django.utils import timezone
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

import factory


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_staff = False
    is_superuser = False
    is_active = True
    date_joined = factory.Faker("past_datetime", tzinfo=timezone.get_current_timezone())
    last_login = factory.Faker("past_datetime", tzinfo=timezone.get_current_timezone())
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")
