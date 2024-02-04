from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from agendable import celery_app
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from restapi.factories import (
    CustomUserFactory,
    MeetingFactory,
    MeetingRecurrenceFactory,
)
from restapi.models import Meeting, MeetingRecurrence
from restapi.serializers import MeetingRecurrenceSerializer


class MeetingViewSetTestCase(TestCase):
    def setUp(self):
        celery_app.conf.update(
            CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True
        )
        self.client = APIClient()
        self.user = CustomUserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.meeting = MeetingFactory()
        self.recurrence = MeetingRecurrenceFactory()
        self.meeting_data = {
            "title": self.meeting.title,
            "start_date": self.meeting.start_date,
            "end_date": self.meeting.end_date,
            "duration": self.meeting.duration,
            "notes": self.meeting.notes,
        }

    def test_get_meeting(self):
        response = self.client.get("/api/meetings/" + str(self.meeting.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.meeting.title)

    def test_add_meeting_recurrence(self):
        response = self.client.post(
            f"/api/meetings/{self.meeting.id}/add_recurrence/",
            data={"recurrence": self.recurrence.id},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_complete_action(self):
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

    def test_get_next_occurrence(self):
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

    def test_create_meeting(self):
        response = self.client.post("/api/meetings/", self.meeting_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Meeting.objects.count(), 2)
        new_meeting = Meeting.objects.latest("id")
        self.assertNotEqual(new_meeting.id, self.meeting.id)
        self.assertEqual(new_meeting.title, self.meeting_data["title"])

    def test_list_meetings(self):
        response = self.client.get("/api/meetings/")
        self.assertEqual(response.status_code, 200)
