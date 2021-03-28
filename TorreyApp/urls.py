from django.urls import path

from . import views

urlpatterns = [
    path('', views.loginPage, name='login'),
    path('signup/', views.signup, name='signup'),
    path('home/', views.homePage, name='home')
]