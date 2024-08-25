from datetime import datetime
from typing import Optional

from meetings.schemas.meeting_recurrence import MeetingRecurrenceSchema
from ninja import Schema


class MeetingSchema(Schema):
    id: int
    recurrence: Optional[MeetingRecurrenceSchema]
    title: str
    start_date: datetime
    end_date: datetime
    duration: int
    location: str
    notes: str
    num_reschedules: int
    reminder_sent: bool
    created_at: datetime
