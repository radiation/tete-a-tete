import logging
from unittest.mock import patch

from django.urls import reverse
from meetings.factories import (
    MeetingFactory,
    MeetingRecurrenceFactory,
    MeetingTaskFactory,
    TaskFactory,
)
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.factories import CustomUserFactory

logger = logging.getLogger(__name__)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class MeetingViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Creating the user with a hashed password
        cls.user = CustomUserFactory()

    def setUp(self):
        # Log in the user for each test
        self.client = APIClient()
        self.user = CustomUserFactory()
        # For JWT auth
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        # Prepare other data and URLs
        self.meeting = MeetingFactory()
        self.recurrence = MeetingRecurrenceFactory(meeting=self.meeting)
        self.task = TaskFactory()
        self.meeting_task = MeetingTaskFactory(meeting=self.meeting, task=self.task)

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
        response = self.client.post(url, recurrence_data, format="json")

        logger.debug(f"\n\nResponse status: {response.status_code}")
        logger.debug(f"\n\nResponse data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_get_meeting_recurrence(self):
        response = self.client.get(
            self.meeting_recurrence_url, {"meeting_id": self.meeting.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.meeting.recurrence.id)

    def test_get_next_occurrence(self):
        url = reverse("meeting-get-next-occurrence")
        response = self.client.get(url, {"meeting_id": self.meeting.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn("next_occurrence_date", response.data)

    @patch("common.tasks.create_or_update_batch.delay")
    def test_complete_meeting(self, mock_create_or_update_batch):
        url = reverse("meeting-complete", kwargs={"pk": self.meeting.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_create_or_update_batch.assert_called_once()
