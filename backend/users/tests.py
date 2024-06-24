import json
from datetime import datetime
from unittest.mock import MagicMock, patch

from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from meetings.factories import MeetingAttendeeFactory, MeetingFactory, TaskFactory
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from users.calendar_services import get_calendar_service, sync_meetings_to_calendar
from users.factories import CustomUserFactory
from users.serializers import UserSerializer

User = get_user_model()


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
        self.url = reverse("user-dashboard")  # Update with the actual URL name

        # Create sample tasks and meetings
        TaskFactory.create_batch(5, assignee=self.user)
        MeetingAttendeeFactory.create_batch(3, user=self.user)

    def test_user_dashboard_response(self):
        response = self.client.get(self.url)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("profile", response_data)
        self.assertIn("tasks", response_data)
        self.assertIn("meetings", response_data)
        self.assertEqual(len(response_data["tasks"]), 5)
        self.assertEqual(len(response_data["meetings"]), 3)
        self.assertEqual(response_data["profile"]["email"], self.user.email)

    def test_user_dashboard_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CalendarViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("users.views.sync_meetings_to_calendar")
    def test_sync_calendar_view(self, mock_sync_meetings_to_calendar):
        MeetingFactory()

        response = self.client.get(reverse("sync_calendar"))

        self.assertEqual(response.status_code, 200)
        mock_sync_meetings_to_calendar.assert_called_once()
        self.assertContains(response, "Meetings synced to Google Calendar")


class TestCalendarServices(TestCase):
    def setUp(self):
        self.user = CustomUserFactory()
        self.social_app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test-client-id",
            secret="test-secret",
        )
        self.social_app.sites.add(settings.SITE_ID)
        self.social_account = SocialAccount.objects.create(
            user=self.user, provider="google", uid="12345"
        )
        self.social_token = SocialToken.objects.create(
            account=self.social_account,
            token="fake-access-token",
            app=self.social_app,
        )
        self.meeting = MeetingFactory.create(
            start_date=timezone.make_aware(datetime(2024, 6, 25, 10, 0, 0)),
            end_date=timezone.make_aware(datetime(2024, 6, 25, 11, 0, 0)),
        )
        self.meeting_attendee = MeetingAttendeeFactory.create(
            meeting=self.meeting, user=self.user
        )

    @patch("users.calendar_services.build")
    def test_get_calendar_service(self, MockBuild):
        get_calendar_service(self.user)

        MockBuild.assert_called_once()
        called_args, called_kwargs = MockBuild.call_args
        self.assertEqual(called_args, ("calendar", "v3"))
        self.assertIn("credentials", called_kwargs)
        self.assertEqual(called_kwargs["credentials"].token, "fake-access-token")

    @patch("users.calendar_services.get_calendar_service")
    def test_sync_meetings_to_calendar(self, mock_get_calendar_service):
        mock_service = MagicMock()
        mock_get_calendar_service.return_value = mock_service

        sync_meetings_to_calendar(self.user)

        mock_service.events().insert.assert_called_once()
        call_args = mock_service.events().insert.call_args[1]["body"]
        self.assertEqual(call_args["summary"], self.meeting.title)
        self.assertEqual(call_args["description"], self.meeting.notes)
        self.assertEqual(
            call_args["start"]["dateTime"], self.meeting.start_date.isoformat()
        )
        self.assertEqual(
            call_args["end"]["dateTime"], self.meeting.end_date.isoformat()
        )
