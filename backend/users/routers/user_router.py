from typing import List

from django.shortcuts import get_object_or_404
from ninja import HTTPException, Router
from users.models import CustomUser
from users.schemas.user import UserSchema

router = Router()


@router.get("/", response=List[UserSchema])
async def list_users(request):
    users = CustomUser.objects.all()
    return users


@router.get("/{user_id}", response=UserSchema)
async def get_user(request, user_id: int):
    user = get_object_or_404(CustomUser, id=user_id)
    return user


@router.post("/", response=UserSchema)
async def create_user(request, user: UserSchema):
    if CustomUser.objects.filter(email=user.email).exists():
        raise HTTPException(
            status_code=400, detail="A user with this email already exists."
        )
    db_user = CustomUser(**user.dict())
    db_user.save()
    return db_user


@router.put("/{user_id}", response=UserSchema)
async def update_user(request, user_id: int, data: UserSchema):
    db_user = get_object_or_404(CustomUser, id=user_id)
    if (
        data.email != db_user.email
        and CustomUser.objects.filter(email=data.email).exists()
    ):
        raise HTTPException(
            status_code=400, detail="A user with this email already exists."
        )
    for attr, value in data.dict().items():
        setattr(db_user, attr, value)
    db_user.save()
    return db_user


@router.delete("/{user_id}", response={204: None})
async def delete_user(request, user_id: int):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return 204
