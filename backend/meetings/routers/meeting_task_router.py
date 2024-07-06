from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from ..models import MeetingTask
from ..schemas.meeting_task import MeetingTaskSchema

router = Router()


@router.get("/", response=List[MeetingTaskSchema])
def list_meeting_tasks(request):
    tasks = MeetingTask.objects.select_related("meeting", "task").all()
    return tasks


@router.get("/by-meeting/{meeting_id}", response=List[MeetingTaskSchema])
def list_tasks_by_meeting(request, meeting_id: int):
    meeting_tasks = MeetingTask.objects.filter(meeting_id=meeting_id).select_related(
        "meeting", "task"
    )
    return meeting_tasks


@router.post("/", response=MeetingTaskSchema)
def create_meeting_task(request, meeting_task: MeetingTaskSchema):
    db_meeting_task = MeetingTask(**meeting_task.dict(exclude_unset=True))
    db_meeting_task.save()
    return db_meeting_task


@router.get("/{meeting_task_id}", response=MeetingTaskSchema)
def get_meeting_task(request, meeting_task_id: int):
    task = get_object_or_404(MeetingTask, id=meeting_task_id)
    return task
