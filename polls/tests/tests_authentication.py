"""Test cases for model."""
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from polls.models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the.
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    end = time + abs(datetime.timedelta(days=days))

    return (Question.objects.create(
        question_text=question_text, pub_date=time, end_date=end))


class AuthenticationTest(TestCase):
    """A Question index page tests."""

    def setUp(self):
        self.user = User.objects.create_user('Miko',
                                        email='Japanese@gmail.com',
                                        password='Himitsu')

        self.user.first_name = "Miko"
        self.user.last_name = "Hato"
        self.user.save()

    def test_logging_in(self):

        self.client.login(username='Miko', password='Himitsu')
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, self.user.first_name)



