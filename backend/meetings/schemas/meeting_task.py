from datetime import datetime
from typing import Optional

from ninja import Schema

from .meeting import MeetingSchema
from .task import TaskSchema


class MeetingTaskSchema(Schema):
    id: Optional[int]
    meeting_id: int
    task_id: int
    created_at: datetime
    meeting_detail: Optional[MeetingSchema] = None  # Nested Meeting details
    task_detail: Optional[TaskSchema] = None  # Nested Task details
