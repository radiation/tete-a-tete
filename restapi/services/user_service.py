
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

    # Additional methods for other user-related functionalities
