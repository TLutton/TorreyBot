from django.contrib.auth import login, authenticate
from django.http import HttpResponseBadRequest
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import GolferUpdateForm
from .utils import TorreyUtils
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)  
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def loginPage(request):
    logger.error("Login view")
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=raw_password)
            if user:
                logger.error("User logging in!")
                login(request, user)
                return redirect('home')
            else:
                logger.error("Invalid user credentials!")
        else:
            logger.error("Form was invalid.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required(login_url='')
def homePage(request):
    user = request.user
    logger.error("homepage")
    if request.method == "POST":
        logger.error("In post")
        form = GolferUpdateForm(data=request.POST )
        if form.is_valid():
            logger.error("Golfer Update form valid.")
            user.golfer.email = form.cleaned_data.get("email")
            user.golfer.send_notifications = form.cleaned_data.get("email_notifs")
            user.golfer.num_players = form.cleaned_data.get("min_players")
            user.golfer.torrey_south = form.cleaned_data.get("torrey_south")
            user.golfer.torrey_north = form.cleaned_data.get("torrey_north")
            user.save()
            return HttpResponseRedirect(reverse("home"))
        else:
            logger.error("Golfer Update form invalid.")
    else:
        form = GolferUpdateForm(initial={
            "email": user.golfer.email,
            "email_notifs": user.golfer.send_notifications,
            "min_players": user.golfer.num_players,
            "torrey_south": user.golfer.torrey_south,
            "torrey_north": user.golfer.torrey_north
        })
    logger.error("Rendering home")
    return render(request, 'home.html', {'form': form})

def teeTrigger(request):
    # TODO: Expect secret text in POST
    if request.method == "POST" or request.method == "GET":
        logger.error("Got trigger!")
        helper = TorreyUtils.TorreyUtils()
        all_times = helper.get_times()
        active_users = User.objects.filter(golfer__send_notifications=True)
        if all_times:
            for active in active_users:
                num_players = active.golfer.num_players
                courses = []
                if active.golfer.torrey_north:
                    courses.append("torrey_north")
                if active.golfer.torrey_south:
                    courses.append("torrey_south")
                if courses:
                    msg_body = helper.filter_times(all_times, {"num_players": active.golfer.num_players, "courses": courses})
                    if msg_body:
                        logger.error("Found appropriate times. Sending email.")
                        helper.send_notification(msg_body, active.golfer.email)
                    else:
                        logger.error("No appropriate times found.")
        else:
            logger.error("Failed to get any tee times!")
        return render(request, 'trigger.html', {'timesData': all_times})
    else:
        return HttpResponseBadRequest(request)
