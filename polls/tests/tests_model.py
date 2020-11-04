"""Test cases for model."""

import datetime
from django.test import TestCase
from django.utils import timezone
from polls.models import Question


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