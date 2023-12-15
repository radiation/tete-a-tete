from celery import Celery, shared_task
from celery.schedules import crontab
from django import test

from .models import CustomUser
from .serializers import *

app = Celery()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )

    # Send reminders every morning at 9am
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        send_reminder.s(),
    )

# Send periodic emails to users with outstanding action items
@shared_task
def send_reminder():
    pass

# Send email asynchronously based on meeting time or due date
@shared_task
def send_email():
    pass

@shared_task
def create_record(serializer):
    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        return serializer.errors
    
@shared_task
def update_user(data):
    user = CustomUser.objects.get(pk=data.get('id'))
    serializer = UserSerializer(user, data=data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        return serializer.errors
    
@shared_task
def create_meeting(serializer, scheduler, attendee):
    if serializer.is_valid():
        serializer.save(scheduler=scheduler, attendee=attendee)
        return serializer.data
    else:
        return serializer.errors
    
@shared_task
def update_meeting(data):
    meeting = Meeting.objects.get(pk=data.get('id'))
    serializer = MeetingNestedSerializer(meeting, data=data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        return serializer.errors
    
@shared_task
def create_actionitem(serializer, meeting, assignee):
    if serializer.is_valid():
        serializer.save(meeting=meeting, assignee=assignee)
        return serializer.data
    else:
        return serializer.errors
    
@shared_task
def update_actionitem(data):
    actionitem = ActionItem.objects.get(pk=data.get('id'))
    serializer = ActionItemNestedSerializer(actionitem, data=data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        return serializer.errors
    
@shared_task
def create_questionanswer(serializer, question, asker, answerer):
    if serializer.is_valid():
        serializer.save(question=question, asker=asker, answerer=answerer)
        return serializer.data
    else:
        return serializer.errors
    
@shared_task
def update_questionanswer(data):
    questionanswer = QuestionAnswer.objects.get(pk=data.get('id'))
    serializer = QuestionAnswerNestedSerializer(questionanswer, data=data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        return serializer.errors

@shared_task
def create_agendaitem(serializer, meeting):
    if serializer.is_valid():
        serializer.save(meeting=meeting)
        return serializer.data
    else:
        return serializer.errors
    
@shared_task
def update_agendaitem(data):
    agendaitem = AgendaItem.objects.get(pk=data.get('id'))
    serializer = AgendaItemNestedSerializer(agendaitem, data=data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        return serializer.errors