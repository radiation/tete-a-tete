from typing import List

from django.shortcuts import get_object_or_404
from meetings.models import Meeting, MeetingAttendee
from meetings.schemas import MeetingAttendeeSchema, MeetingSchema
from ninja import Router

router = Router()


@router.get("/", response=List[MeetingAttendeeSchema])
def list_attendees(request):
    attendees = MeetingAttendee.objects.select_related("meeting", "user").all()
    return attendees


@router.get("/{attendee_id}", response=MeetingAttendeeSchema)
def get_attendee(request, attendee_id: int):
    attendee = get_object_or_404(MeetingAttendee, id=attendee_id)
    return attendee


@router.post("/", response=MeetingAttendeeSchema)
def create_attendee(request, attendee: MeetingAttendeeSchema):
    db_attendee = MeetingAttendee(**attendee.dict(exclude_unset=True))
    db_attendee.save()
    return db_attendee


@router.get("/by-meeting/{meeting_id}", response=List[MeetingAttendeeSchema])
def list_attendees_by_meeting(request, meeting_id: int):
    attendees = MeetingAttendee.objects.filter(meeting_id=meeting_id).select_related(
        "meeting", "user"
    )
    return attendees


@router.get("/by-user/{user_id}", response=List[MeetingSchema])
def list_meetings_by_user(request, user_id: int):
    meetings = Meeting.objects.filter(meetingattendee__user_id=user_id).distinct()
    return meetings
