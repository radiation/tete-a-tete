from django.db import models
    
class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email_address = models.CharField(max_length=50)

class Meeting(models.Model):    
    scheduler = models.ForeignKey(User, related_name="meetings_scheduler_related", on_delete=models.CASCADE)
    attendee = models.ForeignKey(User, related_name="meetings_attendee_related", on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    num_reschedules = models.IntegerField(default=0)

class ActionItem(models.Model):
    meeting = models.ForeignKey(Meeting, related_name="actionitems_meeting_related", on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, related_name="actionitems_assignee_related", on_delete=models.CASCADE)
    completed = models.BooleanField()
    todo_item = models.TextField()

class Question(models.Model):
    question_text = models.TextField()

class QuestionAnswer(models.Model):
    question = models.ForeignKey(Question, related_name="questionanswers_question_related", on_delete=models.CASCADE)
    asker = models.ForeignKey(User, related_name="questions_asker_related", on_delete=models.CASCADE)
    answerer = models.ForeignKey(User, related_name="questions_answerer_related", on_delete=models.CASCADE)
    answer_text = models.TextField()
    
