"""A configuration of view for poll sites."""
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages

from polls.forms import CreateUserForm
from .models import Choice, Question, Vote

# Create your views here.

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s: &(name)s:%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


class IndexView(generic.ListView):
    """A view of index page."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions.

        (not including those set to be published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


class DetailView(generic.DetailView):
    """A view of detail page."""

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """A view of result page."""

    model = Question
    template_name = 'polls/results.html'


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
            logger.info("Login Attempt: Unsuccessful login as {} at {}".format(request.POST['username'],
                                                                               request.META.get('REMOTE_ADDR')))
            return redirect('polls:login')
        # what if form is not valid?
        # we should display a message in signup.html
    else:
        form = CreateUserForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_page(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('polls:index')

    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info("Login Attempt: Successful login as {} at {}".format(request.user.username,
                                                                             request.META.get('REMOTE_ADDR')))
            return redirect('polls:index')
        else:
            messages.info(request, 'Username or Password is incorrect')
            logger.warning("Login Attempt: Unsuccessful login as {} at {}".format(request.POST['username'],
                                                                                  request.META.get('REMOTE_ADDR')))
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_page(request):
    """"Logout page"""
    logout(request)
    return redirect('polls:login')


@login_required
def vote(request, question_id):
    """Do allowed users vote due to the conditions."""
    question = get_object_or_404(Question, pk=question_id)

    if question.can_vote():
        try:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the question voting form.
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
            })
        else:
            in_vote = Vote.objects.filter(question=question_id, user=request.user).exists()
            if in_vote:
                voting = Vote.objects.get(user=request.user)
                voting.choice_id = selected_choice.id
                voting.save()
            else:
                voting = Vote.objects.create(question=question, user=request.user, choice=selected_choice)
                voting.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse(
                'polls:results', args=(question.id,)))
    else:
        messages.error(request, "This poll was not in the polling period.")
        return redirect('poll:index')
