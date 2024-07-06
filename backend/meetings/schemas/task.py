from datetime import datetime
from typing import Optional

from ninja import Schema
from users.schemas.user import UserSchema


class TaskSchema(Schema):
    id: Optional[int]
    assignee: int
    assignee_detail: Optional[UserSchema]
    title: str
    description: str
    due_date: Optional[datetime]
    completed: bool
    completed_date: Optional[datetime]
    created_at: datetime
