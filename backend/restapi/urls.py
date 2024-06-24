from django.urls import path
from rest_framework.routers import DefaultRouter
from restapi.views import (
    MeetingAttendeeViewSet,
    MeetingRecurrenceViewSet,
    MeetingTaskViewSet,
    MeetingViewSet,
    TaskViewSet,
    health,
)

router = DefaultRouter()
router.register(r"meetings", MeetingViewSet, basename="meeting")
router.register(
    r"meeting_recurrences", MeetingRecurrenceViewSet, basename="meeting-recurrence"
)
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"meeting_tasks", MeetingTaskViewSet, basename="meeting-task")
router.register(
    r"meeting_attendees", MeetingAttendeeViewSet, basename="meeting-attendee"
)

urlpatterns = [
    path("health/", health, name="health"),
]

urlpatterns += router.urls
