from meetings.routers.meeting_router import router as meeting_router
from meetings.routers.recurrence_router import router as recurrence_router
from meetings.routers.task_router import router as task_router
from ninja import NinjaAPI

api = NinjaAPI()
api.add_router("/meetings", meeting_router)
api.add_router("/recurrences", recurrence_router)
api.add_router("/tasks", task_router)
