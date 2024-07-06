from typing import List

from django.shortcuts import get_object_or_404
from models import MeetingRecurrence
from ninja import Router
from schemas.recurrence import MeetingRecurrenceSchema

router = Router()


@router.get("/", response=List[MeetingRecurrenceSchema])
async def list_recurrences(request):
    return MeetingRecurrence.objects.all()


@router.get("/{recurrence_id}", response=MeetingRecurrenceSchema)
async def get_recurrence(request, recurrence_id: int):
    recurrence = get_object_or_404(MeetingRecurrence, id=recurrence_id)
    return recurrence


@router.post("/", response=MeetingRecurrenceSchema)
async def create_recurrence(request, recurrence: MeetingRecurrenceSchema):
    db_recurrence = MeetingRecurrence(**recurrence.dict())
    db_recurrence.save()
    return db_recurrence


@router.put("/{recurrence_id}", response=MeetingRecurrenceSchema)
async def update_recurrence(request, recurrence_id: int, data: MeetingRecurrenceSchema):
    db_recurrence = get_object_or_404(MeetingRecurrence, id=recurrence_id)
    for attr, value in data.dict().items():
        setattr(db_recurrence, attr, value)
    db_recurrence.save()
    return db_recurrence


@router.delete("/{recurrence_id}", response={204: None})
async def delete_recurrence(request, recurrence_id: int):
    db_recurrence = get_object_or_404(MeetingRecurrence, id=recurrence_id)
    db_recurrence.delete()
    return 204
