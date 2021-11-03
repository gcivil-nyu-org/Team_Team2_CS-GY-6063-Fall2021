from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text="Required")

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "profilename",
            "accessible",
            "family_friendly",
            "transaction_not_required",
        ]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]
