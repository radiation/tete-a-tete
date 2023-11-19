from django.db import models
    
class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email_address = models.CharField(max_length=50)
    def __str__(self):
        return self.field1

class Meeting(models.Model):    
    scheduler = models.ForeignKey(User, related_name="meetings_scheduler_related", on_delete=models.CASCADE)
    attendee = models.ForeignKey(User, related_name="meetings_attendee_related", on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    def __str__(self):
        return self.field1

class ActionItem(models.Model):
    meeting = models.ForeignKey(Meeting, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    completed = models.BooleanField()
    todo_item = models.TextField()
    def __str__(self):
        return self.field1

class MeetingModelManager(models.Manager):
    def get_objects_based_on_query(self, your_condition):
        return self.filter(your_column=your_condition)

