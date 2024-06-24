from celery import shared_task
from .calendar_services import sync_meetings_to_calendar


@shared_task
def sync_calendar_task():
    sync_meetings_to_calendar()
