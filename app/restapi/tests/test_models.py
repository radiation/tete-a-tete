from django.test import TestCase
from restapi.models import *

user_john=User.objects.create(
    first_name="John", 
    last_name="Doe", 
    email_address="john.doe@example.com"
)
user_jane=User.objects.create(
    first_name="Jane", 
    last_name="Doe", 
    email_address="jane.doe@example.com"
)
meeting_jj=Meeting.objects.create(scheduler=user_john, attendee=user_jane, start_date="2022-01-01", end_date="2022-01-02")
action_item = ActionItem.objects.create(meeting=meeting_jj, assignee=user_john, completed=False, todo_item="Do something")
question = Question.objects.create(question_text="What is your favorite color?")
question_answer = QuestionAnswer.objects.create(question=question, asker=user_john, answerer=user_jane, answer_text="Blue")
agenda_item = AgendaItem.objects.create(meeting=meeting_jj, title="Agenda Item Title", description="Agenda Item Description")

class UserModelTest(TestCase):
    def test_user_creation(self):
        self.assertEqual(user_john.user_name, "john_doe")
        self.assertEqual(user_john.first_name, "John")
        self.assertEqual(user_john.last_name, "Doe")
        self.assertEqual(user_john.email_address, "john.doe@example.com")

class MeetingModelTest(TestCase):
    def test_meeting_creation(self):
        self.assertEqual(meeting_jj.scheduler, user_john)
        self.assertEqual(meeting_jj.attendee, user_jane)
        self.assertEqual(meeting_jj.start_date, "2022-01-01")
        self.assertEqual(meeting_jj.end_date, "2022-01-02")
        self.assertEqual(meeting_jj.num_reschedules, 0)

class ActionItemModelTest(TestCase):
    def test_action_item_creation(self):
        self.assertEqual(action_item.meeting, meeting_jj)
        self.assertEqual(action_item.assignee, user_john)
        self.assertFalse(action_item.completed)
        self.assertEqual(action_item.todo_item, "Do something")

class QuestionModelTest(TestCase):
    def test_question_creation(self):
        self.assertEqual(question.question_text, "What is your favorite color?")

class QuestionAnswerModelTest(TestCase):
    def test_question_answer_creation(self):
        self.assertEqual(question_answer.question, question)
        self.assertEqual(question_answer.asker, user_john)
        self.assertEqual(question_answer.answerer, user_jane)
        self.assertEqual(question_answer.answer_text, "Blue")

class AgendaItemModelTest(TestCase):
    def test_agenda_item_creation(self):
        self.assertEqual(agenda_item.meeting, meeting_jj)
        self.assertEqual(agenda_item.title, "Agenda Item Title")
        self.assertEqual(agenda_item.description, "Agenda Item Description")