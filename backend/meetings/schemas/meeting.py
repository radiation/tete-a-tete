from datetime import datetime
from typing import Optional

from ninja import Schema


class MeetingRecurrenceSchema(Schema):
    id: int
    frequency: str
    week_day: Optional[int]
    month_week: Optional[int]
    interval: int
    end_recurrence: Optional[datetime]
    created_at: datetime


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
