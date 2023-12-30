from restapi.models import Task

def mark_complete(task_id):
    task = Task.objects.get(pk=task_id)
    task.completed = True
    task.save()