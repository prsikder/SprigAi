from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from .models import User, DISTRICT_CHOICES


class SprigSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    district = forms.ChoiceField(choices=[("", "Select your district")] + DISTRICT_CHOICES, required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone", "district", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data.get("last_name", "")
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone", "")
        user.district = self.cleaned_data.get("district", "")
        if commit:
            user.save()
        return user


class SprigLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")


class SprigAdminLoginForm(AuthenticationForm):
    """Separate login form used on the admin login page for a distinct visual flow."""
    username = forms.CharField(label="Admin Username")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "district", "profile_image"]
        widgets = {
            "district": forms.Select(),
        }


class SprigPasswordChangeForm(PasswordChangeForm):
    pass
