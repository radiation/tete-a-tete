from django.db import models
    
class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email_address = models.CharField(max_length=100, unique=True)
    user_name = models.CharField(default="", max_length=50, unique=True)
    def save(self, *args, **kwargs):
        if self.user_name == "":
            self.user_name = self.first_name.lower() + "_" + self.last_name.lower()
        super(User, self).save(*args, **kwargs)
    def __str__(self):
        return self.first_name + " " + self.last_name

class Meeting(models.Model):    
    scheduler = models.ForeignKey(User, related_name="meetings_scheduler_related", on_delete=models.CASCADE)
    attendee = models.ForeignKey(User, related_name="meetings_attendee_related", on_delete=models.CASCADE)
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
    
class AgendaItem(models.Model):
    meeting = models.ForeignKey(Meeting, related_name="agendaitems_meeting_related", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(default="")
