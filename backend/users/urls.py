from django.urls import path
from ninja import NinjaAPI
from users.routers.user_router import router as user_router

api = NinjaAPI()
api.add_router("/users", user_router)

urlpatterns = [
    path("api/", api.urls),  # API endpoints for the users app
]
