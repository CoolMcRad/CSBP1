from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import render_to_string
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.db import connection

from .models import Choice, Question, Vote

# Create your views here.

from django.http import HttpResponse


def IndexView(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    user_votes = Vote.objects.filter(user=request.user.id).values_list(
        "question_id", flat=True
    )

    context = {
        "latest_question_list": latest_question_list,
        "voted_question_ids": list(user_votes),
    }
    return render(request, "polls/index.html", context)


def AllPollsView(request):
    question_list = Question.objects.order_by("-pub_date")
    user_votes = Vote.objects.filter(user=request.user.id).values_list(
        "question_id", flat=True
    )

    context = {
        "question_list": question_list,
        "voted_question_ids": list(user_votes),
    }
    return render(request, "polls/all_polls.html", context)


def DetailView(request, question_id):
    try:
        question = get_object_or_404(Question, pk=question_id)
        user_votes = Vote.objects.filter(user=request.user.id).values_list(
            "question_id", flat=True
        )
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    context = {
        "question": question,
        "voted_question_ids": list(user_votes),
    }
    return render(request, "polls/detail.html", context)


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    success_url = "/login"
    template_name = "polls/register.html"


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    user = request.user

    #if Vote.objects.filter(user=user, question=question).exists():
    #   return HttpResponseForbidden(render_to_string("polls/unauthorized.html"))

    try:
        # selected_choice = question.choice_set.get(pk=request.POST["choice"])
        selected_choice = question.choice_set.get(pk=request.GET.get("choice"))
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        Vote.objects.create(user=user, question=question, choice=selected_choice)
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def CreatePollView(request):
    if request.method == "POST":
        question_text = request.POST.get("question")
        choice_texts = request.POST.getlist("choices")

        if question_text and choice_texts:

            #    with connection.cursor() as cursor:
            #        query = f"INSERT INTO polls_question (question_text, pub_date) VALUES ('{question_text}', '{timezone.now()}')"
            #        cursor.execute(query)

            question = Question.objects.create(
                question_text=question_text, pub_date=timezone.now()
            )
            for choice_text in choice_texts:
                if choice_text.strip():
                    Choice.objects.create(
                        question=question, choice_text=choice_text.strip()
                    )
            #            with connection.cursor() as cursor:
            #                cursor.execute(
            #                    "SELECT id FROM polls_question WHERE question_text = %s",
            #                    [question_text],
            #                )
            #                row = cursor.fetchone()
            #                query2 = f"INSERT INTO polls_choice (question_id, choice_text, votes) VALUES ('{row[0]}', '{choice_text.strip()}', '{0}')"
            #                cursor.execute(query2)

            return HttpResponseRedirect(reverse("polls:index"))

    return render(request, "polls/create_poll.html")


# You can use this to try sql injection
# LIMIT 0; 'UNION SELECT id, username, password FROM auth_user --
def SearchView(request):
    query = request.GET.get("q", "")
    results = []

    if query:
        # results = Question.objects.filter(question_text__icontains=query)
        # uncomment line above, then comment from here... --------
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM polls_question WHERE question_text LIKE '%{query}%'"
            )
            rows = cursor.fetchall()
        results = [
            {"id": row[0], "question_text": row[1], "pub_date": row[2]} for row in rows
        ]
        # ...to here --------
    context = {
        "query": query,
        "question_list": results,
    }
    return render(request, "polls/search.html", context)


@staff_member_required
# @login_required
def secret(request):
    return render(request, "polls/secret.html")


def UnauthorizedView(request):
    return render(request, "polls/unauthorized.html")


def HomePageView(request):
    return render(request, "polls/index.html")
