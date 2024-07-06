from datetime import datetime
from typing import Optional

from ninja import Field, Schema
from ninja.errors import ValidationError
from users.models import CustomUser


class UserSchema(Schema):
    id: Optional[int]
    email: str = Field(..., regex=r"^\S+@\S+\.\S+$")  # Ensuring email format
    first_name: Optional[str]
    last_name: Optional[str]
    is_staff: bool
    is_superuser: bool
    is_active: bool
    date_joined: datetime

    @Field.validator("email")
    def validate_email(cls, value):
        if CustomUser.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists.")
        return value
