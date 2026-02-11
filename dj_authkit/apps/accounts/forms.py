from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group

from dj_authkit.apps.accounts.models import GroupProfile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "phone_number")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "phone_number")
