from django.test import TestCase
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from restapi.models import *
from restapi.serializers import *
from restapi.factories import CustomUserFactory, MeetingFactory

class UserSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_instance = CustomUserFactory()
        cls.serializer = UserSerializer(instance=cls.user_instance)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {'id', 'email', 'first_name', 'last_name', 'password', 
                           'is_staff', 'is_active', 'is_superuser', 
                           'date_joined', 'last_login',
                           'groups', 'user_permissions',
                           }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(data['email'], self.user_instance.email)

    def test_deserialization_and_validation(self):
        user_data = {
            'email': 'newuser@example.com',
            'password': 'password',
            'first_name': 'John',
            'last_name': 'Doe',
        }
        serializer = UserSerializer(data=user_data)
        if not serializer.is_valid():
            print(serializer.errors)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.email, user_data['email'])

    def test_invalid_deserialization(self):
        invalid_data = {
            'email': 'invalidemail',
        }
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

class MeetingSerializerTest(TestCase):

    @classmethod
    def setUpTestData(self):
        self.meeting_instance = MeetingFactory()
        self.serializer = MeetingSerializer(instance=self.meeting_instance)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'title', 'start_date', 'end_date', 'notes', 'num_reschedules', 'created_at']))

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(data['title'], self.meeting_instance.title)
        self.assertEqual(parse_datetime(data['start_date']), self.meeting_instance.start_date)
        self.assertEqual(parse_datetime(data['end_date']), self.meeting_instance.end_date)
        self.assertEqual(data['notes'], self.meeting_instance.notes)

    def test_deserialization(self):
        data = {
            'title': 'New Meeting',
            'start_date': self.meeting_instance.start_date,
            'end_date': self.meeting_instance.end_date,
            'notes': 'New Meeting Notes'
        }
        serializer = MeetingSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        new_meeting = serializer.save()
        self.assertEqual(new_meeting.title, data['title'])
        self.assertEqual(new_meeting.start_date, data['start_date'])
        self.assertEqual(new_meeting.end_date, data['end_date'])
        self.assertEqual(new_meeting.notes, data['notes'])

    def test_invalid_deserialization(self):
        invalid_data = {
            'title': '',
        }
        serializer = MeetingSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

