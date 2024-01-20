from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from restapi.factories import *
from restapi.serializers import MeetingRecurrenceSerializer, MeetingSerializer
from unittest.mock import patch, ANY
from restapi.tasks import create_or_update_record

User = get_user_model()

class MeetingViewSetTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='email@example.com', password='password')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.meeting = MeetingFactory()
        self.meeting_data = {
            'title': self.meeting.title,
            'start_date': self.meeting.start_date,
            'end_date': self.meeting.end_date,
            'duration': self.meeting.duration,
            'notes': self.meeting.notes,
            'recurrence': self.meeting.recurrence.id
        }

    def test_get_meeting(self):
        response = self.client.get('/api/meetings/' + str(self.meeting.id) + '/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], self.meeting.title)

    @patch('restapi.tasks.create_or_update_record.delay')
    def test_complete_action(self, mock_complete_meeting):
        response = self.client.post('/api/meetings/complete/', {'meeting_id': self.meeting.id})
        self.assertEqual(response.status_code, 200)
        mock_complete_meeting.assert_called_with(ANY, 'Meeting', create=True)

    def test_get_meeting_recurrence(self):
        response = self.client.get('/api/meetings/get_meeting_recurrence/', {'meeting_id': self.meeting.id})
        self.assertEqual(response.status_code, 200)

        expected_data = MeetingRecurrenceSerializer(self.meeting.recurrence).data
        self.assertEqual(response.data, expected_data)

    '''def test_get_next_occurrence(self):
        response = self.client.get('/api/meetings/get_next_occurrence/', {'meeting_id': self.meeting.id})
        if response.status_code == 200:
            expected_data = MeetingSerializer(self.meeting.get_next_occurrence()).data
            self.assertEqual(response.data, expected_data)
        else:
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)'''

    @patch('restapi.tasks.create_or_update_record.delay')
    def test_create_meeting(self, mock_create_meeting):
        response = self.client.post('/api/meetings/', self.meeting_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Meeting.objects.count(), 2)  # Assuming one is already created in setUp
        new_meeting = Meeting.objects.latest('id')
        self.assertNotEqual(new_meeting.id, self.meeting.id)
        self.assertEqual(new_meeting.title, self.meeting_data['title'])

    def test_list_meetings(self):
        # Create some meetings in the test setup
        response = self.client.get('/api/meetings/')
        self.assertEqual(response.status_code, 200)
        # Assert that the response data contains the meetings'''
