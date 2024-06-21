import datetime
from django.db import IntegrityError
from django.test import TestCase
from common.constants import FREQUENCY_CHOICES, MONTH_WEEK_CHOICES, WEEKDAY_CHOICES
from restapi.factories import (
    MeetingFactory,
    MeetingRecurrenceFactory,
    MeetingAttendeeFactory,
    TaskFactory,
    MeetingTaskFactory,
)
from users.models import CustomUser
from restapi.models import Meeting, MeetingTask, Task
from restapi.services import MeetingService

import logging

logger = logging.getLogger(__name__)


class MeetingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.meeting = MeetingFactory()

    def test_meeting_title(self):
        self.assertTrue(isinstance(self.meeting.title, str))
        self.assertTrue(len(self.meeting.title) > 0)

    def test_meeting_str(self):
        meeting = MeetingFactory(
            title="Board Meeting", start_date=datetime.datetime(2023, 5, 15, 14, 30)
        )
        self.assertEqual(str(meeting), "2023-05-15 14:30:00: Board Meeting")

    def test_meeting_dates(self):
        self.assertTrue(isinstance(self.meeting.start_date, datetime.datetime))
        self.assertEqual(
            self.meeting.end_date,
            self.meeting.start_date + datetime.timedelta(minutes=30),
        )

    def test_meeting_additional(self):
        self.assertTrue(isinstance(self.meeting.notes, str))
        self.assertTrue(len(self.meeting.notes) > 0)
        self.assertEqual(self.meeting.num_reschedules, 0)

    def test_get_next_occurrence(self):
        next_meeting = MeetingService.get_next_occurrence(self.meeting)

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
        self.assertIn(
            self.meeting_recurrence.week_day,
            self.weekday_values,
            "Weekday is not in WEEKDAY_CHOICES",
        )
        self.assertIn(
            self.meeting_recurrence.month_week,
            self.month_week_values,
            "Month week is not in MONTH_WEEK_CHOICES",
        )
        self.assertIn(
            self.meeting_recurrence.frequency,
            self.frequency_values,
            "Frequency is not in FREQUENCY_CHOICES",
        )
        self.assertTrue(isinstance(self.meeting_recurrence.interval, int))

    def test_meeting_recurrence_str(self):
        recurrence = MeetingRecurrenceFactory(frequency="daily")
        expected_str = (
            f"Daily recurrence starting {recurrence.created_at.strftime('%Y-%m-%d')}"
        )
        self.assertEqual(str(recurrence), expected_str)


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

    def test_task_completion(self):
        completed_at = datetime.datetime.now(datetime.timezone.utc)
        task = TaskFactory(completed=True, completed_date=completed_at)
        self.assertEqual(task.completed_date, completed_at)

        # Test setting to not completed clears the date
        task.completed = False
        task.save()
        self.assertIsNone(task.completed_date)


class MeetingTaskModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.meeting_task = MeetingTaskFactory()

    def test_meeting_task_fields(self):
        logger.debug(f"MeetingTask: {self.meeting_task}")
        self.assertTrue(isinstance(self.meeting_task.meeting, Meeting))
        self.assertTrue(isinstance(self.meeting_task.task, Task))
        self.assertTrue(isinstance(self.meeting_task.created_at, datetime.datetime))

    def test_meeting_task_uniqueness(self):
        # Create an initial MeetingTask instance
        with self.assertRaises(IntegrityError):
            MeetingTaskFactory(
                meeting=self.meeting_task.meeting, task=self.meeting_task.task
            )

    def test_cascade_delete_to_meeting_task_from_meeting(self):
        # Testing cascade delete when a Meeting is deleted
        meeting_id = self.meeting_task.meeting.id
        self.meeting_task.meeting.delete()
        with self.assertRaises(MeetingTask.DoesNotExist):
            MeetingTask.objects.get(meeting_id=meeting_id)

    def test_cascade_delete_to_meeting_task_from_task(self):
        # Testing cascade delete when a Task is deleted
        task_id = self.meeting_task.task.id
        self.meeting_task.task.delete()
        with self.assertRaises(MeetingTask.DoesNotExist):
            MeetingTask.objects.get(task_id=task_id)
