from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from users.models import CustomUser
from users.factories import CustomUserFactory
from restapi.factories import (
    MeetingFactory,
    MeetingAttendeeFactory,
    MeetingRecurrenceFactory,
    TaskFactory,
)
from restapi.models import Task, Meeting, MeetingAttendee
from restapi.services import meeting_service
from restapi.serializers import (
    MeetingSerializer,
    MeetingRecurrenceSerializer,
    TaskSerializer,
)

from unittest.mock import patch
from rest_framework import status


class MeetingViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Creating the user with a hashed password
        cls.user = CustomUserFactory()

    def setUp(self):
        # Log in the user for each test
        self.client.login(email=self.user.email, password="defaultpassword")

        # Prepare other data and URLs
        self.meeting = MeetingFactory()
        self.recurrence = MeetingRecurrenceFactory(meeting=self.meeting)

        self.meeting_recurrence_url = reverse("meeting-get-meeting-recurrence")
        self.next_occurrence_url = reverse("meeting-get-next-occurrence")

    @patch("common.tasks.create_or_update_record.delay")
    def test_create_meeting(self, mock_create_or_update):
        # Define the data for creating a new meeting
        meeting_data = {
            "title": "Board Meeting",
            "notes": "Quarterly review",
            "start_date": "2024-01-01T10:00:00Z",
            "end_date": "2024-01-01T11:00:00Z",
        }

        response = self.client.post(reverse("meeting-list"), meeting_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create_or_update.assert_called_once()

    @patch("common.tasks.create_or_update_record.delay")
    def test_add_recurrence(self, mock_create_or_update):
        url = reverse("meeting-add-recurrence", kwargs={"pk": self.meeting.id})
        recurrence_data = {"recurrence_id": self.recurrence.id}
        response = self.client.post(url, recurrence_data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        meeting_serializer = MeetingSerializer(instance=self.meeting)
        recurrence_serializer = MeetingRecurrenceSerializer(instance=self.recurrence)
        expected_meeting_data = meeting_serializer.data
        expected_meeting_data["recurrence"] = recurrence_serializer.data
        mock_create_or_update.assert_called_once_with(
            expected_meeting_data, "Meeting", create=False
        )

    """
    def test_get_meeting_recurrence(self):
        response = self.client.get(
            self.meeting_recurrence_url, {"meeting_id": self.meeting.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print(self.recurrence)
        self.assertEqual(response.data["id"], self.recurrence.id)


    def test_get_next_occurrence(self):
        url = reverse("meeting-get-next-occurrence")
        response = self.client.get(url, {"meeting_id": self.meeting.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # You will need to modify the assertion to match the structure of your actual response
        self.assertIn("next_occurrence_date", response.data)

    @patch("common.tasks.complete_meeting.delay")
    def test_complete_meeting(self, mock_complete_meeting):
        url = reverse("meeting-complete", kwargs={"pk": self.meeting.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_complete_meeting.assert_called_once()
    """
