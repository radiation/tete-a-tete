import datetime

from django.test import TestCase
from meetings.factories import MeetingFactory
from meetings.schemas import MeetingSchema


class MeetingSchemaTest(TestCase):
    def test_meeting_schema_with_factory(self):
        # Create a meeting instance with valid data
        meeting = MeetingFactory.create()

        # Convert the meeting instance to schema
        meeting_data = MeetingSchema.from_orm(meeting).dict()

        # Validate the data through schema
        validated_data = MeetingSchema(**meeting_data)
        self.assertEqual(validated_data.title, meeting.title)
        self.assertIsNotNone(validated_data.start_date)

    def test_meeting_schema_end_date_validation(self):
        # Create a meeting with end_date before start_date
        meeting = MeetingFactory.create(
            start_date=datetime.datetime.now(),
            end_date=datetime.datetime.now() - datetime.timedelta(hours=2),
        )

        # This should raise a validation error due to end_date being before start_date
        with self.assertRaises(ValueError):
            MeetingSchema.from_orm(meeting)
