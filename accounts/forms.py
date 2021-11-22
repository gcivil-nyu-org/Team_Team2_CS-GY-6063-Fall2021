from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from naturescall.models import Rating
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError

class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        print(email)
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError(
                    "There is no user registered with the specified E-Mail address."
                    )
            return email

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


class EditRating(forms.ModelForm):
    headline = forms.CharField(widget=forms.TextInput(attrs={"size": 80}))
    comment = forms.CharField(widget=forms.TextInput(attrs={"size": 80}))

    class Meta:
        model = Rating
        fields = ["rating", "headline", "comment"]
