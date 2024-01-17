import sys
from django.apps import AppConfig


class RestapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restapi'

'''
    def ready(self):
        if 'test' in sys.argv or 'makemigrations' in sys.argv or 'migrate' in sys.argv:
            return

        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        # Create an interval schedule for every 5 seconds
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=5,  # every 5 seconds
            period=IntervalSchedule.SECONDS,
        )

        # Create or update the periodic task
        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='Send email every 5 seconds',
            task='restapi.tasks.send_meeting_reminders',
        )
'''