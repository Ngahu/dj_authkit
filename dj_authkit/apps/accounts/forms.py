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


class GroupCreateForm(forms.Form):
    name = forms.CharField(max_length=150)
    description = forms.CharField(widget=forms.Textarea, required=False)

    def clean_name(self):
        name = self.cleaned_data["name"]

        if Group.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A group with this name already exists.")

        return name

    def save(self):
        group = Group.objects.create(name=self.cleaned_data["name"])
        GroupProfile.objects.create(
            group=group, description=self.cleaned_data.get("description")
        )
        return group
