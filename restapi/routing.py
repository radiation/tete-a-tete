import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from restapi import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agendable.settings")

urlpatterns = [
    path("ws/task_status/<task_id>/", consumers.TaskStatusConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "websocket": URLRouter(urlpatterns),
        # (http->django views is added by default)
    }
)
