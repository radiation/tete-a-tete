from django.urls import path
from ninja import NinjaAPI

from .routers.meeting_attendee_router import router as meeting_attendee_router
from .routers.meeting_router import router as meeting_router
from .routers.meeting_task_router import router as meeting_task_router
from .routers.recurrence_router import router as recurrence_router
from .routers.task_router import router as task_router

api = NinjaAPI()
api.add_router("/meetings", meeting_router)
api.add_router("/recurrences", recurrence_router)
api.add_router("/meeting_attendees", meeting_attendee_router)
api.add_router("/meeting-tasks", meeting_task_router)
api.add_router("/tasks", task_router)

urlpatterns = [
    path("api/", api.urls),
]
