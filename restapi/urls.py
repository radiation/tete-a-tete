from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"meetings", MeetingViewSet)
router.register(r"meeting_recurrences", MeetingRecurrenceViewSet)
router.register(r"tasks", TaskViewSet)
router.register(r"meeting_tasks", MeetingTaskViewSet)
router.register(r"meeting_attendees", MeetingAttendeeViewSet)

urlpatterns = router.urls
