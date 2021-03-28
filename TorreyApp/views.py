from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from .forms import GolferUpdateForm
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

