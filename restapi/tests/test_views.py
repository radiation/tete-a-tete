import time
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from restapi.factories import *
from restapi.models import Meeting
from restapi.serializers import MeetingRecurrenceSerializer
from restapi.test_utils import mock_create_or_update_record
from unittest.mock import patch, ANY

User = get_user_model()


class MeetingViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="email@example.com", password="password"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.meeting = MeetingFactory()
        self.meeting_data = {
            "title": self.meeting.title,
            "start_date": self.meeting.start_date,
            "end_date": self.meeting.end_date,
            "duration": self.meeting.duration,
            "notes": self.meeting.notes,
            "recurrence": self.meeting.recurrence.id,
        }

    def test_get_meeting(self):
        response = self.client.get("/api/meetings/" + str(self.meeting.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.meeting.title)

    @patch("restapi.tasks.create_or_update_record.delay")
    def test_complete_action(self, mock_task):
        mock_task.side_effect = mock_create_or_update_record
        response = self.client.post(
            "/api/meetings/complete/", {"meeting_id": self.meeting.id}
        )
        self.assertEqual(response.status_code, 200)

    def test_get_meeting_recurrence(self):
        response = self.client.get(
            "/api/meetings/get_meeting_recurrence/", {"meeting_id": self.meeting.id}
        )
        self.assertEqual(response.status_code, 200)

        expected_data = MeetingRecurrenceSerializer(self.meeting.recurrence).data
        self.assertEqual(response.data, expected_data)

    @patch("restapi.tasks.create_or_update_record.delay")
    def test_get_next_occurrence(self, mock_task):
        mock_task.side_effect = mock_create_or_update_record

        response = self.client.get(
            "/api/meetings/get_next_occurrence/", {"meeting_id": self.meeting.id}
        )
        self.assertEqual(response.status_code, 202)
        recent_meeting = Meeting.objects.latest("created_at")
        self.assertIsNotNone(recent_meeting, "Meeting was not created")

        self.assertEqual(recent_meeting.title, self.meeting.title)
        self.assertTrue(
            timezone.now() >= recent_meeting.created_at, "Timestamp is incorrect"
        )

    @patch("restapi.tasks.create_or_update_record.delay")
    def test_create_meeting(self, mock_task):
        mock_task.side_effect = mock_create_or_update_record
        response = self.client.post("/api/meetings/", self.meeting_data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Meeting.objects.count(), 2)
        new_meeting = Meeting.objects.latest("id")
        self.assertNotEqual(new_meeting.id, self.meeting.id)
        self.assertEqual(new_meeting.title, self.meeting_data["title"])

    def test_list_meetings(self):
        response = self.client.get("/api/meetings/")
        self.assertEqual(response.status_code, 200)
