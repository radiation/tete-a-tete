import datetime
from django.test import TestCase
from restapi.factories import CustomUserFactory, MeetingFactory, MeetingAttendeeFactory, MeetingTaskFactory, TaskFactory
from restapi.models import CustomUser, Meeting, Task

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