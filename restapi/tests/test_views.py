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
        # Additional setup for other tests

    @patch("common.tasks.create_or_update_record.delay")
    def test_create_meeting(self, mock_create_or_update):
        # Define the data for creating a new meeting
        meeting_data = {
            "title": "Board Meeting",
            "notes": "Quarterly review",
            "start_date": "2024-01-01T10:00:00Z",
            "end_date": "2024-01-01T11:00:00Z",
        }

        # Make the POST request
        response = self.client.post(reverse("meeting-list"), meeting_data)

        # Check that the response status code is HTTP 201_CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Additionally, ensure the mock was called, if the task's execution is significant to the test
        mock_create_or_update.assert_called_once()

    @patch("common.tasks.add_recurrence_to_meeting.delay")
    def test_add_recurrence(self, mock_add_recurrence):
        url = reverse("meeting-add-recurrence", kwargs={"pk": self.meeting.id})
        recurrence_data = {"recurrence_id": self.recurrence.id}
        response = self.client.post(url, recurrence_data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_add_recurrence.assert_called_once_with(self.meeting.id, self.recurrence.id)

    def test_get_meeting_recurrence(self):
        url = reverse("meeting-get-meeting-recurrence")
        response = self.client.get(url, {"meeting_id": self.meeting.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ensure the data returned is correct (you may need to adjust this based on actual returned structure)
        self.assertEqual(
            response.data["recurrence_pattern"], self.meeting.recurrence.pattern
        )

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
