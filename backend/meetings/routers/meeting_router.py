from typing import List

from django.shortcuts import get_object_or_404
from models import Meeting, MeetingRecurrence
from ninja import NinjaAPI, Router
from schemas.meeting import MeetingSchema
from services import MeetingService

api = NinjaAPI()
router = Router()


@router.get("/meetings", response=List[MeetingSchema])
async def list_meetings(request):
    meetings = Meeting.objects.select_related("recurrence").all()
    return meetings


@router.get("/meetings/{meeting_id}", response=MeetingSchema)
async def get_meeting(request, meeting_id: int):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    return meeting


@router.post("/meetings/{meeting_id}/complete", response={204: None})
async def complete_meeting(request, meeting_id: int):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    MeetingService.complete_meeting(meeting.id)  # Adjust your service logic accordingly
    return 204


@router.post("/meetings/{meeting_id}/add-recurrence", response=MeetingSchema)
async def add_recurrence(request, meeting_id: int, recurrence_id: int):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    recurrence = get_object_or_404(MeetingRecurrence, id=recurrence_id)
    meeting.recurrence = recurrence
    meeting.save()
    return meeting


api.add_router("/api/", router)
