from django.utils import timezone
from common.tasks import (
    create_or_update_record,
    create_or_update_batch,
)
from restapi.models import (
    Meeting,
    MeetingTask,
    Task,
)
import logging

from restapi.utils import get_next_occurrence_date

logger = logging.getLogger(__name__)


class MeetingService:

    # Return a meeting object based on the recurrence
    @staticmethod
    def get_next_occurrence(meeting):
        """
        Retrieves the next occurrence of a meeting based on its recurrence pattern.
        If there is no subsequent meeting found, attempts to create one.
        """
        logger.debug(f"Finding next occurrence for {meeting.title}")
        try:
            # Attempt to find the next occurrence in the database
            next_meeting = (
                Meeting.objects.filter(
                    recurrence=meeting.recurrence, start_date__gt=meeting.start_date
                )
                .order_by("start_date")
                .first()
            )

            if next_meeting:
                logger.debug(f"Next meeting found: {next_meeting}")
                return next_meeting
            elif meeting.recurrence:
                logger.debug(
                    f"No next meeting found for {meeting.title}. Creating one."
                )
                MeetingService.create_next_meeting(meeting)
        except Exception as e:
            logger.error(f"Failed to retrieve or create the next occurrence: {str(e)}")

        # Explicitly return None if no next occurrence exists
        return None

    @staticmethod
    def create_next_meeting(meeting):

        next_occurrence_time = get_next_occurrence_date(
            meeting.recurrence, meeting.start_date
        )
        if next_occurrence_time and (
            not meeting.recurrence.end_recurrence
            or next_occurrence_time <= meeting.recurrence.end_recurrence
        ):
            duration = meeting.end_date - meeting.start_date
            logger.debug(
                f"Creating next meeting for {meeting.title} at {next_occurrence_time}"
            )
            meeting_data = {
                "recurrence": meeting.recurrence,
                "title": meeting.title,
                "start_date": next_occurrence_time,
                "end_date": next_occurrence_time + duration,
                "notes": meeting.notes,
                "num_reschedules": meeting.num_reschedules,
                "created_at": timezone.now(),
            }
            create_or_update_record.delay(meeting_data, "Meeting", create=True)

    @staticmethod
    def complete_meeting(meeting_id):

        meeting = Meeting.objects.get(pk=meeting_id)
        next_occurrence = MeetingService.get_next_occurrence(meeting)

        if next_occurrence:
            tasks_data = []
            meeting_tasks = MeetingTask.objects.filter(meeting__id=meeting_id)

            for meeting_task in meeting_tasks:
                task_data = {"id": meeting_task.id, "meeting": next_occurrence}
                tasks_data.append(task_data)

            if tasks_data:
                logger.debug(
                    f"Sending the following data for batch processing: {tasks_data}"
                )
                create_or_update_batch.delay(tasks_data, "MeetingTask")

                # Return meeting id for next occurrence for further processing
                return next_occurrence.id

        else:
            return None

    @staticmethod
    def generate_reminder(meeting_id, user_id):

        open_tasks = MeetingTask.objects.filter(meeting__id=meeting_id, completed=False)
        meeting = Meeting.objects.get(pk=meeting_id)
        notes = meeting.notes


class TaskService:
    @staticmethod
    def mark_complete(task_id):

        task = Task.objects.get(pk=task_id)
        task.completed = True
        task.save()
