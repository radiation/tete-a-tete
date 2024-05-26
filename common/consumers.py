import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.generic.websocket import WebsocketConsumer
from celery.result import AsyncResult


def get_task_info(task_id):
    task = AsyncResult(task_id)
    state = task.state

    if state == "FAILURE":
        error = str(task.result)
        response = {
            "state": state,
            "error": error,
        }
    else:
        response = {
            "state": state,
        }
    return response


def notify_channel_layer(task_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        task_id, {"type": "update_task_status", "data": get_task_info(task_id)}
    )


class TaskStatusConsumer(WebsocketConsumer):
    def connect(self):
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]

        async_to_sync(self.channel_layer.group_add)(self.task_id, self.channel_name)

        self.accept()

        self.send(text_data=json.dumps(get_task_info(self.task_id)))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.task_id, self.channel_name)

    def update_task_status(self, event):
        data = event["data"]

        self.send(text_data=json.dumps(data))
