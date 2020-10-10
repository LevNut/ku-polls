"""Model configuration for polls application."""

import datetime
from django.db import models
from django.utils import timezone

# Create your models here.


class Question (models.Model):
    """A model class that contains a method about question in polls."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    end_date = models.DateTimeField("end date")

    def __str__(self):
        """Given readable string representation of an object."""
        return self.question_text

    def is_published(self):
        """
        Check that the polls is already published or not.

        Returns:
            bool: The return value. True if it already published, False if not.
        """
        now = timezone.now()
        if now >= self.pub_date:
            return True
        return False

    def can_vote(self):
        """
        Check if the polls is able to vote or not.

        Returns:
            bool: The return value. True for the avaliable published poll , False if not.
        """
        now = timezone.now()
        if self.pub_date <= now < self.end_date:
            return True
        return False

    def was_published_recently(self):
        """Check that the polls is recently published or not."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    """A choice model class."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Given readable string representation of an object."""
        return self.choice_text
