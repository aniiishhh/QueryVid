from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Answers
import json
from .utils import *


@login_required
def index(request):
    return render(request, "index.html")


@csrf_exempt
def generate_answer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            yt_link = data["link"]
            question = data["question"]

        except (KeyError, json.JSONDecodeError):
            return JsonResponse({"error": "Invalid data sent"}, status=400)

        # get yt title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({"error": " Failed to get transcript"}, status=500)

        # use OpenAI to generate the blog
        answer = get_answer(transcription, question)

        # save answer
        new_answer = Answers.objects.create(
            user=request.user,
            video_title=title,
            question=question,
            video_link=yt_link,
            answer=answer,
        )

        new_answer.save()

        return JsonResponse({"content": answer})

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
def query_history(request):

    answers = Answers.objects.filter(user=request.user)
    context = {"answers": answers}

    return render(request, "history.html", context)


@login_required
def answer_detail(request, pk):
    detail = Answers.objects.get(id=pk)

    if request.user == detail.user:
        context = {"detail": detail}
        return render(request, "answer.html", context)
    else:
        redirect("/")


def app_login(request):

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")

        else:
            context = {
                "error": "Username and Password do not match. Please try Logging in again or Sign Up for a new account."
            }
            return render(request, "login.html", context)

    return render(request, "login.html")


def app_signup(request):

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm-password"]

        if password == confirm_password:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect("/")
            except:
                error = "Try signing up again with a different username and fill all the fields."
                context = {"error": error}
                return render(request, "signup.html", context)

        else:
            error = "Passwords do not match. Please try again."
            context = {"error": error}
            return render(request, "signup.html", context)

    return render(request, "signup.html")


@login_required
def app_logout(request):
    logout(request)
    return redirect("/")
