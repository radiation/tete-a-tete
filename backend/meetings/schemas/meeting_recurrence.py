from datetime import datetime
from typing import Optional

from ninja import Schema


class MeetingRecurrenceSchema(Schema):
    id: Optional[int]
    frequency: str
    week_day: Optional[int]
    month_week: Optional[int]
    interval: int
    end_recurrence: Optional[datetime]
    created_at: datetime
