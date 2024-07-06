from datetime import datetime
from typing import List

from django.shortcuts import get_object_or_404
from meetings.models import Task
from meetings.schemas.task import TaskSchema
from ninja import Router

router = Router()


@router.get("/", response=List[TaskSchema])
async def list_tasks(request):
    tasks = Task.objects.select_related("assignee").all()
    return tasks


@router.get("/{task_id}", response=TaskSchema)
async def get_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    return task


@router.post("/", response=TaskSchema)
async def create_task(request, task: TaskSchema):
    db_task = Task(**task.dict(exclude_unset=True))
    db_task.save()
    return db_task


@router.put("/{task_id}", response=TaskSchema)
async def update_task(request, task_id: int, data: TaskSchema):
    db_task = get_object_or_404(Task, id=task_id)
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(db_task, attr, value)
    db_task.save()
    return db_task


@router.post("/{task_id}/mark-complete", response={204: None})
async def mark_complete(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    task.completed = True
    task.completed_date = datetime.now()
    task.save()
    return 204


@router.get("/by-user/{user_id}", response=List[TaskSchema])
async def list_by_user(request, user_id: int):
    tasks = Task.objects.filter(assignee_id=user_id).select_related("assignee")
    return tasks
