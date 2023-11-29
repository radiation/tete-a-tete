from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class Meeting(models.Model):    
    scheduler = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="meetings_scheduler_related", on_delete=models.CASCADE)
    attendee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="meetings_attendee_related", on_delete=models.CASCADE)
    title = models.CharField(default="", max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    num_reschedules = models.IntegerField(default=0)
    def save(self, *args, **kwargs):
        if self.title == "":
            self.title = str(self.scheduler) + " / " + str(self.attendee)+ " / " + str(self.start_date)
        super(Meeting, self).save(*args, **kwargs)

class ActionItem(models.Model):
    meeting = models.ForeignKey(Meeting, related_name="actionitems_meeting_related", on_delete=models.CASCADE)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="actionitems_assignee_related", on_delete=models.CASCADE)
    completed = models.BooleanField()
    todo_item = models.TextField()

class Question(models.Model):
    question_text = models.TextField()

class QuestionAnswer(models.Model):
    question = models.ForeignKey(Question, related_name="questionanswers_question_related", on_delete=models.CASCADE)
    asker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="questions_asker_related", on_delete=models.CASCADE)
    answerer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="questions_answerer_related", on_delete=models.CASCADE)
    answer_text = models.TextField()
    
class AgendaItem(models.Model):
    meeting = models.ForeignKey(Meeting, related_name="agendaitems_meeting_related", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(default="")
