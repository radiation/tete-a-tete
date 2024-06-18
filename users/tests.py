from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from users.factories import CustomUserFactory
from users.serializers import UserSerializer
from restapi.factories import TaskFactory, MeetingAttendeeFactory
from unittest.mock import patch
import json


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUserFactory()

    def test_user_email(self):
        self.assertIsNotNone(self.user.email)
        self.assertIn("@", self.user.email)

    def test_user_name(self):
        self.assertTrue(self.user.first_name.isalpha())
        self.assertTrue(self.user.last_name.isalpha())

    def test_user_attributes(self):
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)


class UserSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_instance = CustomUserFactory()
        cls.serializer = UserSerializer(instance=cls.user_instance)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
            "last_login",
            "groups",
            "user_permissions",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(data["email"], self.user_instance.email)

    def test_deserialization_and_validation(self):
        user_data = {
            "email": "newuser@example.com",
            "password": "password",
            "first_name": "John",
            "last_name": "Doe",
        }
        serializer = UserSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.email, user_data["email"])

    def test_invalid_deserialization(self):
        invalid_data = {
            "email": "invalidemail",
        }
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class UsersManagersTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email="normal@user.com", password="foo")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            email="super@user.com", password="foo"
        )
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com", password="foo", is_superuser=False
            )

class UserDashboardTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('user-dashboard')  # Update with the actual URL name

        # Create sample tasks and meetings
        TaskFactory.create_batch(5, assignee=self.user)
        MeetingAttendeeFactory.create_batch(3, user=self.user)

    def test_user_dashboard_response(self):
        response = self.client.get(self.url)
        response_data = json.loads(response.content)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile', response_data)
        self.assertIn('tasks', response_data)
        self.assertIn('meetings', response_data)
        self.assertEqual(len(response_data['tasks']), 5)
        self.assertEqual(len(response_data['meetings']), 3)
        self.assertEqual(response_data['profile']['email'], self.user.email)

    def test_user_dashboard_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)