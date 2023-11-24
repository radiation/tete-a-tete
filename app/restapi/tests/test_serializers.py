from django.test import TestCase
from restapi.models import *
from restapi.serializers import *

class UserSerializerTestCase(TestCase):
    def test_user_serializer(self):
        user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email_address': 'john_doe@example.com',
            'user_name': 'john_doe'
        }
        serializer = UserFlatSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.user_name, 'john_doe')
        self.assertEqual(user.email_address, 'john_doe@example.com')

class MeetingSerializerTestCase(TestCase):
    def test_meeting_serializer(self):
        scheduler_data = {
            'first_name': 'George',
            'last_name': 'Washington',
            'email_address': 'falseteeth@us.gov',
            'user_name': 'george_washington'
        }
        attendee_data = {
            'first_name': 'Abraham',
            'last_name': 'Lincoln',
            'email_address': 'fourscore@us.gov',
            'user_name': 'abraham_lincoln'
        }
        meeting_data = {
            'scheduler': scheduler_data,
            'attendee': attendee_data,
            'start_date': "2022-01-01",
            'end_date': "2022-01-02"
        }
        serializer = MeetingNestedSerializer(data=meeting_data)
        print(serializer.is_valid())
        print(serializer.errors)
        self.assertTrue(serializer.is_valid())
        meeting = serializer.save()
        self.assertEqual(str(meeting.scheduler), "George Washington")
        self.assertEqual(str(meeting.attendee), "Abraham Lincoln")
        self.assertEqual(meeting.title, "George Washington / Abraham Lincoln / 2022-01-01 00:00:00+00:00")

# Add more test cases for other serializers

class ActionItemSerializerTestCase(TestCase):
    pass

class QuestionSerializerTestCase(TestCase):
    pass

class QuestionAnswerSerializerTestCase(TestCase):
    pass
