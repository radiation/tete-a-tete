from celery import Celery

app = Celery("agendable")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "sync-calendar-every-hour": {
        "task": "restapi.tasks.sync_calendar_task",
        "schedule": 3600.0,  # sync every hour
    },
}
