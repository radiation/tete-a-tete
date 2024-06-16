from restapi.models import MeetingAttendee

class UserService:
    def __init__(self, user):
        self.user = user

    def update_preferences(self, preferences):
        # Update user preferences
        self.user.preferences = preferences
        self.user.save()

    def send_email(self, subject, message, from_email):
        from restapi.tasks import send_email_to_user

        if self.user.email:
            send_email_to_user.delay(subject, message, from_email, self.user.email)

    def get_user_tasks(user):
        return list(user.task_set.values('id', 'title', 'description', 'status'))

    def get_user_meetings(user):
        return list(MeetingAttendee.objects.filter(user=user).select_related('meeting').values(
            'meeting__id', 'meeting__title', 'meeting__scheduled_time'))
