from django.test import TestCase
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from restapi.models import *
from restapi.serializers import *
from restapi.factories import (
    CustomUserFactory,
    MeetingFactory,
    MeetingRecurrenceFactory,
    MeetingAttendeeFactory,
    MeetingTaskFactory,
    TaskFactory,
)


class UserSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_instance = CustomUserFactory()
        cls.serializer = UserSerializer(instance=cls.user_instance)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
            "last_login",
            "groups",
            "user_permissions",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(data["email"], self.user_instance.email)

    def test_deserialization_and_validation(self):
        user_data = {
            "email": "newuser@example.com",
            "password": "password",
            "first_name": "John",
            "last_name": "Doe",
        }
        serializer = UserSerializer(data=user_data)
        if not serializer.is_valid():
            logger.error(serializer.errors)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.email, user_data["email"])

    def test_invalid_deserialization(self):
        invalid_data = {
            "email": "invalidemail",
        }
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class MeetingSerializerTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.meeting_instance = MeetingFactory()
        self.serializer = MeetingSerializer(instance=self.meeting_instance)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            set(
                [
                    "id",
                    "title",
                    "recurrence",
                    "duration",
                    "start_date",
                    "end_date",
                    "notes",
                    "num_reschedules",
                    "reminder_sent",
                    "created_at",
                ]
            ),
        )

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(data["title"], self.meeting_instance.title)
        self.assertEqual(
            parse_datetime(data["start_date"]), self.meeting_instance.start_date
        )
        self.assertEqual(
            parse_datetime(data["end_date"]), self.meeting_instance.end_date
        )
        self.assertEqual(data["notes"], self.meeting_instance.notes)

    def test_deserialization(self):
        data = {
            "title": "New Meeting",
            "start_date": self.meeting_instance.start_date,
            "end_date": self.meeting_instance.end_date,
            "notes": "New Meeting Notes",
        }
        serializer = MeetingSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        new_meeting = serializer.save()
        self.assertEqual(new_meeting.title, data["title"])
        self.assertEqual(new_meeting.start_date, data["start_date"])
        self.assertEqual(new_meeting.end_date, data["end_date"])
        self.assertEqual(new_meeting.notes, data["notes"])

    def test_invalid_deserialization(self):
        invalid_data = {
            "title": "",
        }
        serializer = MeetingSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)


class MeetingRecurrenceSerializerTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.meeting_recurrence_instance = MeetingRecurrenceFactory()
        self.serializer = MeetingRecurrenceSerializer(
            instance=self.meeting_recurrence_instance
        )

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            set(
                [
                    "id",
                    "frequency",
                    "week_day",
                    "month_week",
                    "interval",
                    "end_recurrence",
                    "created_at",
                ]
            ),
        )

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(data["frequency"], self.meeting_recurrence_instance.frequency)
        self.assertEqual(data["week_day"], self.meeting_recurrence_instance.week_day)
        self.assertEqual(
            data["month_week"], self.meeting_recurrence_instance.month_week
        )
        self.assertEqual(data["interval"], self.meeting_recurrence_instance.interval)

    def test_deserialization(self):
        data = {
            "frequency": "daily",
            "week_day": self.meeting_recurrence_instance.week_day,
            "month_week": self.meeting_recurrence_instance.month_week,
            "interval": self.meeting_recurrence_instance.interval,
            "end_recurrence": self.meeting_recurrence_instance.end_recurrence,
        }
        serializer = MeetingRecurrenceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        new_meeting_recurrence = serializer.save()

    def test_invalid_deserialization(self):
        invalid_data = {
            "frequency": "",
        }
        serializer = MeetingRecurrenceSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("frequency", serializer.errors)


class MeetingAttendeeSerializerTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.meeting_attendance_instance = MeetingAttendeeFactory()
        self.serializer = MeetingAttendeeSerializer(
            instance=self.meeting_attendance_instance
        )

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()), set(["id", "meeting", "user", "is_scheduler"])
        )

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(
            data["meeting"]["id"], self.meeting_attendance_instance.meeting.id
        )
        self.assertEqual(data["user"]["id"], self.meeting_attendance_instance.user.id)
        self.assertEqual(
            data["is_scheduler"], self.meeting_attendance_instance.is_scheduler
        )

    def test_deserialization(self):
        data = {
            "meeting": self.meeting_attendance_instance.meeting.id,
            "user": self.meeting_attendance_instance.user.id,
            "is_scheduler": True,
        }
        serializer = MeetingAttendeeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        new_meeting_attendance = serializer.save()
        self.assertEqual(new_meeting_attendance.meeting.id, data["meeting"])
        self.assertEqual(new_meeting_attendance.user.id, data["user"])
        self.assertEqual(new_meeting_attendance.is_scheduler, data["is_scheduler"])

    def test_invalid_deserialization(self):
        invalid_data = {
            "meeting": "",
        }
        serializer = MeetingAttendeeSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("meeting", serializer.errors)


class TaskSerializerTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.task_instance = TaskFactory()
        self.serializer = TaskSerializer(instance=self.task_instance)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            set(
                [
                    "id",
                    "assignee",
                    "title",
                    "description",
                    "due_date",
                    "completed",
                    "completed_date",
                    "created_at",
                ]
            ),
        )

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(data["assignee"]["id"], self.task_instance.assignee.id)
        self.assertEqual(data["title"], self.task_instance.title)
        self.assertEqual(data["description"], self.task_instance.description)
        self.assertEqual(parse_datetime(data["due_date"]), self.task_instance.due_date)
        self.assertEqual(data["completed"], self.task_instance.completed)

    def test_deserialization(self):
        data = {
            "assignee": self.task_instance.assignee.id,
            "title": "New Task",
            "description": "New Task Description",
            "due_date": self.task_instance.due_date,
            "completed": True,
            "completed_date": self.task_instance.completed_date,
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        new_task = serializer.save()
        self.assertEqual(new_task.assignee.id, data["assignee"])
        self.assertEqual(new_task.title, data["title"])
        self.assertEqual(new_task.description, data["description"])
        self.assertEqual(new_task.due_date, data["due_date"])
        self.assertEqual(new_task.completed, data["completed"])
        self.assertEqual(new_task.completed_date, data["completed_date"])

    def test_invalid_deserialization(self):
        invalid_data = {
            "assignee": "",
        }
        serializer = TaskSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("assignee", serializer.errors)


class MeetingTaskSerializerTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.meeting_task_instance = MeetingTaskFactory()
        self.serializer = MeetingTaskSerializer(instance=self.meeting_task_instance)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(["id", "meeting", "task", "created_at"]))

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(data["meeting"]["id"], self.meeting_task_instance.meeting.id)
        self.assertEqual(data["task"]["id"], self.meeting_task_instance.task.id)

    def test_deserialization(self):
        data = {
            "meeting": MeetingFactory().id,
            "task": TaskFactory().id,
        }
        serializer = MeetingTaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        new_meeting_task = serializer.save()
        self.assertEqual(new_meeting_task.meeting.id, data["meeting"])
        self.assertEqual(new_meeting_task.task.id, data["task"])

    def test_invalid_deserialization(self):
        invalid_data = {
            "meeting": "",
        }
        serializer = MeetingTaskSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("meeting", serializer.errors)
