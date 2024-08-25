from django.test import TestCase
from meetings.factories import MeetingFactory
from meetings.models import Meeting
from ninja.testing import TestClient


class MeetingAPITest(TestCase):
    def setUp(self):
        self.client = TestClient()
        # Pre-populate database with 5 meetings
        MeetingFactory.create_batch(5)

    def test_list_meetings_endpoint(self):
        response = self.client.get("/api/meetings/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)

    def test_create_meeting_endpoint(self):
        meeting_data = {
            "title": "New Board Meeting",
            "start_date": "2023-12-25T09:00:00",
            "end_date": "2023-12-25T10:00:00",
            "notes": "Discuss annual budgets",
            "num_reschedules": 0,
            "reminder_sent": False,
        }
        response = self.client.post("/api/meetings/", json=meeting_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "New Board Meeting")
        # Verify that the data is saved in the database
        self.assertTrue(Meeting.objects.filter(title="New Board Meeting").exists())
