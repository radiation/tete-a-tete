from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from allauth.socialaccount.models import SocialToken
from restapi.models import MeetingAttendee

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service(user):
    social_token = SocialToken.objects.filter(
        account__user=user, account__provider="google"
    ).first()
    if not social_token:
        raise Exception("User does not have a valid Google social token")

    creds = Credentials(token=social_token.token)
    service = build("calendar", "v3", credentials=creds)
    return service


def sync_meetings_to_calendar(user):
    service = get_calendar_service(user)
    attendee_meetings = MeetingAttendee.objects.filter(user=user).select_related(
        "meeting"
    )

    for attendee in attendee_meetings:
        meeting = attendee.meeting
        event = {
            "summary": meeting.title,
            "location": "",
            "description": meeting.notes,
            "start": {
                "dateTime": meeting.start_date.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": meeting.end_date.isoformat(),
                "timeZone": "UTC",
            },
        }

        event = service.events().insert(calendarId="primary", body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
