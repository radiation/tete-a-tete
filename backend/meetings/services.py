import logging

from common.tasks import create_or_update_batch
from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now
from meetings.models import Meeting, MeetingTask, Task
from meetings.utils import get_next_occurrence_date

logger = logging.getLogger(__name__)


class MeetingService:
    @staticmethod
    def get_meetings_by_user(user_id):
        meetings = (
            Meeting.objects.filter(Q(meetingattendee__user__id=user_id))
            .distinct()
            .select_related("recurrence")
            .prefetch_related("meetingattendee_set")
        )
        return meetings

    # Return a meeting object based on the recurrence
    @staticmethod
    def get_next_occurrence(meeting):
        logger.debug(f"Finding next occurrence for {meeting}")
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
                next_meeting = MeetingService.create_next_meeting(meeting)
                return next_meeting
        except Exception as e:
            logger.error(f"Failed to retrieve or create the next occurrence: {str(e)}")

        # Explicitly return None if no next occurrence exists
        return None

    @staticmethod
    def create_next_meeting(meeting):
        next_occurrence_date = get_next_occurrence_date(
            meeting.recurrence, meeting.start_date
        )
        if next_occurrence_date and (
            not meeting.recurrence.end_recurrence
            or next_occurrence_date <= meeting.recurrence.end_recurrence
        ):
            duration = meeting.end_date - meeting.start_date
            meeting_data = {
                "recurrence": meeting.recurrence,
                "title": meeting.title,
                "start_date": next_occurrence_date,
                "end_date": next_occurrence_date + duration,
                "notes": meeting.notes,
                "num_reschedules": meeting.num_reschedules,
                "created_at": now(),
            }
            logger.debug(
                f"Creating next meeting for {meeting.title} at {next_occurrence_date}"
            )
            try:
                new_meeting = Meeting.objects.create(**meeting_data)
                logger.debug(f"Next meeting created: {new_meeting}")
                return new_meeting
            except IntegrityError as e:
                logger.error(
                    f"Failed to create the next meeting due "
                    f"to a data integrity issue: {str(e)}"
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error occurred while creating "
                    f"the next meeting: {str(e)}"
                )
        else:
            logger.warning(
                f"No valid occurrence time found or out "
                f"of recurrence range for {meeting.title}"
            )

        return None

    @staticmethod
    def complete_meeting(meeting_id):

        logger.debug(f"Completing meeting {meeting_id}")
        meeting = Meeting.objects.get(pk=meeting_id)
        next_occurrence = MeetingService.get_next_occurrence(meeting)

        logger.debug(f"Next occurrence for {meeting.title}: {next_occurrence}")
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


class TaskService:
    @staticmethod
    def mark_complete(task_id):

        task = Task.objects.get(pk=task_id)
        task.completed = True
        task.save()

    @staticmethod
    def get_tasks_by_user(user_id):
        return Task.objects.filter(assignee__id=user_id)
