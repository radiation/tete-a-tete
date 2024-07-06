from django.urls import path
from ninja import NinjaAPI

from .routers.meeting_router import router as meeting_router
from .routers.recurrence_router import router as recurrence_router

api = NinjaAPI()
api.add_router("/meetings", meeting_router)
api.add_router("/recurrences", recurrence_router)

urlpatterns = [
    path("api/", api.urls),  # API endpoints for the meetings app
]
