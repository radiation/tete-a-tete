from celery import shared_task

from .models import CustomUser
from .serializers import *


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