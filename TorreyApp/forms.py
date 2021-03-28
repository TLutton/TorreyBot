from django.contrib.auth.forms import UserCreationForm, UsernameField
from django import forms
from django.contrib.auth.models import User

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {
            'username': UsernameField,
            'email': forms.EmailField
            }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class GolferUpdateForm(forms.Form):
    email = forms.EmailField(label='email', required=True)
    email_notifs = forms.BooleanField(required=False, label="email_notifs")
    min_players = forms.TypedChoiceField(coerce=int, empty_value=1, choices=[
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
    ], label="min_players", required=True)
    torrey_south = forms.BooleanField(required=False, label="torrey_south")
    torrey_north = forms.BooleanField(required=False, label="torrey_north")
