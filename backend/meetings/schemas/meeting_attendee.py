from typing import Optional

from meetings.schemas.meeting import MeetingSchema
from ninja import Schema
from users.schemas.user import UserSchema


class MeetingAttendeeSchema(Schema):
    meeting_id: int
    user_id: int
    is_scheduler: bool
    meeting_detail: Optional[MeetingSchema] = None  # Nested Meeting details
    user_detail: Optional[UserSchema] = None  # Nested User details
