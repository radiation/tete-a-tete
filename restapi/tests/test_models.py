import datetime
from time import sleep
from django.test import TestCase
from restapi.factories import *
from restapi.models import *
from unittest.mock import patch

class UserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUserFactory()

    def test_user_email(self):
        self.assertIsNotNone(self.user.email)
        self.assertIn('@', self.user.email)

    def test_user_name(self):
        self.assertTrue(self.user.first_name.isalpha())
        self.assertTrue(self.user.last_name.isalpha())

    def test_user_attributes(self):
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

class MeetingModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.meeting = MeetingFactory()

    def test_meeting_title(self):
        self.assertTrue(isinstance(self.meeting.title, str))
        self.assertTrue(len(self.meeting.title) > 0)

    def test_meeting_dates(self):
        self.assertTrue(isinstance(self.meeting.start_date, datetime.datetime))
        self.assertEqual(self.meeting.end_date, self.meeting.start_date + datetime.timedelta(minutes=30))

    def test_meeting_additional(self):
        self.assertTrue(isinstance(self.meeting.notes, str))
        self.assertTrue(len(self.meeting.notes) > 0)
        self.assertEqual(self.meeting.num_reschedules, 0)

    def test_get_next_occurrence(self):
        # Mock the asynchronous task to create a new meeting
        with patch('restapi.tasks.create_or_update_record.delay') as mock_task:
            mock_task.side_effect = lambda meeting_data, model_name, create: (
                Meeting.objects.create(**meeting_data) if create else None
            )

            # Test get_next_occurrence on the existing meeting
            next_meeting = self.meeting.get_next_occurrence()
            self.assertIsNone(next_meeting, "Expected no next meeting yet")

            # Test get_next_occurrence again
            next_meeting = self.meeting.get_next_occurrence()
        
        self.assertIsNotNone(next_meeting, "Expected to find the next meeting")
        self.assertEqual(next_meeting.recurrence, self.meeting.recurrence)
        self.assertGreater(next_meeting.start_date, self.meeting.start_date)

class MeetingRecurrenceModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.meeting_recurrence = MeetingRecurrenceFactory()
        cls.weekday_values = [choice[0] for choice in WEEKDAY_CHOICES]
        cls.month_week_values = [choice[0] for choice in MONTH_WEEK_CHOICES]
        cls.frequency_values = [choice[0] for choice in FREQUENCY_CHOICES]

    def test_meeting_recurrence(self):
        self.assertIn(self.meeting_recurrence.week_day, self.weekday_values, "Weekday is not in WEEKDAY_CHOICES")
        self.assertIn(self.meeting_recurrence.month_week,self.month_week_values, "Month week is not in MONTH_WEEK_CHOICES")
        self.assertIn(self.meeting_recurrence.frequency, self.frequency_values, "Frequency is not in FREQUENCY_CHOICES")
        self.assertTrue(isinstance(self.meeting_recurrence.interval, int))

class MeetingAttendeeModelTest(TestCase):

    @classmethod
    def setUpTestData(self):
        self.meeting_attendance = MeetingAttendeeFactory()

    def test_meeting_attendance(self):
        self.assertTrue(isinstance(self.meeting_attendance.meeting, Meeting))
        self.assertTrue(isinstance(self.meeting_attendance.user, CustomUser))

class TaskModelTest(TestCase):

    @classmethod
    def setUpTestData(self):
        self.task = TaskFactory()

    def test_task_fields(self):
        self.assertTrue(isinstance(self.task.assignee, CustomUser))
        self.assertTrue(isinstance(self.task.title, str))
        self.assertTrue(isinstance(self.task.description, str))
        self.assertTrue(isinstance(self.task.due_date, datetime.datetime))
        self.assertTrue(isinstance(self.task.completed, bool))
        self.assertTrue(isinstance(self.task.created_at, datetime.datetime))

class MeetingTaskModelTest(TestCase):

    @classmethod
    def setUpTestData(self):
        self.meeting_task = MeetingTaskFactory()

    def test_meeting_task_fields(self):
        self.assertTrue(isinstance(self.meeting_task.meeting, Meeting))
        self.assertTrue(isinstance(self.meeting_task.task, Task))
        self.assertTrue(isinstance(self.meeting_task.created_at, datetime.datetime))