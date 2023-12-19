from django.test import TestCase
from restapi.models import *

user_john=CustomUser.objects.create(
    first_name="John", 
    last_name="Doe", 
    email_address="john.doe@example.com"
)
user_jane=CustomUser.objects.create(
    first_name="Jane", 
    last_name="Doe", 
    email_address="jane.doe@example.com"
)
meeting=Meeting.objects.create(scheduler=user_john, attendee=user_jane, start_date="2022-01-01", end_date="2022-01-02")
meeting_attendee_john=MeetingAttendee.objects.create(meeting=meeting, user=user_john, is_scheduler=True)
meeting_attendee_jane=MeetingAttendee.objects.create(meeting=meeting, user=user_jane, is_scheduler=False)
task_john=Task.objects.create(assignee=user_john, title="Task 1", description="Description 1", due_date="2022-01-01", completed=False, completed_date=None, created_at="2021-01-01")
task_jane=Task.objects.create(assignee=user_jane, title="Task 2", description="Description 2", due_date="2022-01-02", completed=False, completed_date=None, created_at="2021-01-02")

class UserModelTest(TestCase):
    def test_user_creation(self):
        self.assertEqual(user_john.user_name, "john_doe")
        self.assertEqual(user_john.first_name, "John")
        self.assertEqual(user_john.last_name, "Doe")
        self.assertEqual(user_john.email_address, "john.doe@example.com")

class MeetingModelTest(TestCase):
    def test_meeting_creation(self):
        self.assertEqual(meeting.scheduler, user_john)
        self.assertEqual(meeting.attendee, user_jane)
        self.assertEqual(meeting.start_date, "2022-01-01")
        self.assertEqual(meeting.end_date, "2022-01-02")
        self.assertEqual(meeting.num_reschedules, 0)

class MeetingAttendeeModelTest(TestCase):
    def test_meeting_attendee_creation(self):
        self.assertEqual(meeting_attendee_john.meeting, meeting)
        self.assertEqual(meeting_attendee_john.user, user_john)
        self.assertEqual(meeting_attendee_jane.user, user_jane)
        self.assertEqual(meeting_attendee_john.is_scheduler, True)
        self.assertEqual(meeting_attendee_jane.is_scheduler, False)

class TaskModelTest(TestCase):
    def test_task_creation(self):
        self.assertEqual(task_john.title, "Task 1")
        self.assertEqual(task_john.description, "Description 1")
        self.assertEqual(task_john.due_date, "2022-01-01")
        self.assertEqual(task_john.completed, False)
        self.assertEqual(task_john.completed_date, None)
        self.assertEqual(task_john.created_at, "2021-01-01")