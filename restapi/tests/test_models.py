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
        self.assertEqual(task_john.created_at, "2021-01-01")from django.test import TestCase
from restapi.models import *

class UserModelTest(TestCase):
    def test_user_creation(self):
        user = CustomUser.objects.create(
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe"
        )
        self.assertEqual(user.email, "john.doe@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

class UserPreferencesModelTest(TestCase):
    def test_user_preferences_creation(self):
        user = CustomUser.objects.create(email="john.doe@example.com")
        preferences = UserPreferences.objects.create(
            user=user,
            timezone="UTC",
            working_days=DaysOfWeek.MONDAY.value,
            working_hours_start="09:00:00",
            working_hours_end="17:00:00"
        )
        self.assertEqual(preferences.user, user)
        self.assertEqual(preferences.timezone, "UTC")
        self.assertEqual(preferences.working_days, DaysOfWeek.MONDAY.value)
        self.assertEqual(preferences.working_hours_start, "09:00:00")
        self.assertEqual(preferences.working_hours_end, "17:00:00")

class EventTimeModelTest(TestCase):
    def test_event_time_creation(self):
        event_time = EventTime.objects.create(
            day=DaysOfWeek.MONDAY.value,
            time="09:00:00"
        )
        self.assertEqual(event_time.day, DaysOfWeek.MONDAY.value)
        self.assertEqual(event_time.time, "09:00:00")

class UserDigestModelTest(TestCase):
    def test_user_digest_creation(self):
        user = CustomUser.objects.create(email="john.doe@example.com")
        event_time = EventTime.objects.create(
            day=DaysOfWeek.MONDAY.value,
            time="09:00:00"
        )
        user_digest = UserDigest.objects.create(
            user=user,
            send_time=event_time
        )
        self.assertEqual(user_digest.user, user)
        self.assertEqual(user_digest.send_time, event_time)

class TaskModelTest(TestCase):
    def test_task_creation(self):
        user = CustomUser.objects.create(email="john.doe@example.com")
        task = Task.objects.create(
            assignee=user,
            title="Task 1",
            description="Description 1",
            due_date="2022-01-01",
            completed=False,
            completed_date=None,
            created_at="2021-01-01"
        )
        self.assertEqual(task.assignee, user)
        self.assertEqual(task.title, "Task 1")
        self.assertEqual(task.description, "Description 1")
        self.assertEqual(task.due_date, "2022-01-01")
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_date)
        self.assertEqual(task.created_at, "2021-01-01")

class MeetingModelTest(TestCase):
    def test_meeting_creation(self):
        meeting = Meeting.objects.create(
            title="Meeting 1",
            start_date="2022-01-01",
            end_date="2022-01-02",
            notes="Some notes",
            num_reschedules=0
        )
        self.assertEqual(meeting.title, "Meeting 1")
        self.assertEqual(meeting.start_date, "2022-01-01")
        self.assertEqual(meeting.end_date, "2022-01-02")
        self.assertEqual(meeting.notes, "Some notes")
        self.assertEqual(meeting.num_reschedules, 0)

class MeetingAttendeeModelTest(TestCase):
    def test_meeting_attendee_creation(self):
        meeting = Meeting.objects.create(
            title="Meeting 1",
            start_date="2022-01-01",
            end_date="2022-01-02",
            notes="Some notes",
            num_reschedules=0
        )
        user = CustomUser.objects.create(email="john.doe@example.com")
        meeting_attendee = MeetingAttendee.objects.create(
            meeting=meeting,
            user=user,
            is_scheduler=True
        )
        self.assertEqual(meeting_attendee.meeting, meeting)
        self.assertEqual(meeting_attendee.user, user)
        self.assertTrue(meeting_attendee.is_scheduler)

class MeetingTaskModelTest(TestCase):
    def test_meeting_task_creation(self):
        meeting = Meeting.objects.create(
            title="Meeting 1",
            start_date="2022-01-01",
            end_date="2022-01-02",
            notes="Some notes",
            num_reschedules=0
        )
        task = Task.objects.create(
            assignee=CustomUser.objects.create(email="john.doe@example.com"),
            title="Task 1",
            description="Description 1",
            due_date="2022-01-01",
            completed=False,
            completed_date=None,
            created_at="2021-01-01"
        )
        meeting_task = MeetingTask.objects.create(
            meeting=meeting,
            task=task
        )
        self.assertEqual(meeting_task.meeting, meeting)
        self.assertEqual(meeting_task.task, task)