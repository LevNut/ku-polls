"""Test cases for model."""

import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Question


# Create your tests here.


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


class QuestionIndexViewTests(TestCase):
    """A Question index page tests."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """Questions with a pub_date in the past are\
            displayed on the index page."""
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """Questions with a pub_date in the future aren't\
             displayed on the index page."""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """Even if both past and future questions exist,\
            only past questions are displayed."""
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionModelTests(TestCase):
    """A test class that test the methods of the Question class."""

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns\
            False for questions whose pub_date. is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns\
            False for questions whose pub_date is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns\
            True for questions whose pub_date is within the last day."""
        time = \
            timezone.now() - datetime.timedelta(hours=23, minutes=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_published_after_end_time(self):
        """Check that the vote is currently allowed after publication date."""
        pub = \
            timezone.now() - datetime.timedelta(hours=23, minutes=59)
        end = pub + abs(datetime.timedelta(hours=22, minutes=59))
        recent_question = Question(pub_date=pub, end_date=end)
        self.assertIs(recent_question.is_published(), True)

    def test_published_before_pub_time(self):
        """Check the vote is currently allowed before publication date."""
        pub = \
            timezone.now() + datetime.timedelta(hours=23, minutes=59)
        end = pub + abs(datetime.timedelta(days=2))
        recent_question = Question(pub_date=pub, end_date=end)
        self.assertIs(recent_question.is_published(), False)

    def test_published_between_pub_and_end_time(self):
        """Check the vote is currently allowed\
            between publication and end date."""
        pub = \
            timezone.now() - datetime.timedelta(hours=23, minutes=59)
        end = pub + abs(datetime.timedelta(days=2))
        recent_question = Question(pub_date=pub, end_date=end)
        self.assertIs(recent_question.is_published(), True)

    def test_vote_after_end_time(self):
        """Test that the user can vote or not after the end time."""
        pub = \
            timezone.now() - datetime.timedelta(hours=23, minutes=59)
        end = pub + abs(datetime.timedelta(hours=22, minutes=59, seconds=59))
        recent_question = Question(pub_date=pub, end_date=end)
        self.assertIs(recent_question.can_vote(), False)

    def test_between_pub_and_end_time(self):
        """Test that the user can vote between pub time and end time."""
        pub = \
            timezone.now() - datetime.timedelta(hours=23, minutes=59)
        end = pub + abs(datetime.timedelta(days=2))
        recent_question = Question(pub_date=pub, end_date=end)
        self.assertIs(recent_question.can_vote(), True)

    def test_vote_before_pub_time(self):
        """Test that the user can vote or not before publish time."""
        pub = \
            timezone.now() + datetime.timedelta(hours=5, minutes=5, seconds=5)
        end = pub + abs(datetime.timedelta(hours=5, minutes=5, seconds=5))
        recent_question = Question(pub_date=pub, end_date=end)
        self.assertIs(recent_question.can_vote(), False)


class QuestionDetailViewTests(TestCase):
    """A Question detail page tests."""

    def test_future_question(self):
        """The detail view of a question with a\
            pub_date in the future returns a 404 not found."""
        future_question = \
            create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """The detail view of a question with a\
            pub_date in the past displays the question's text."""
        past_question = \
            create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
