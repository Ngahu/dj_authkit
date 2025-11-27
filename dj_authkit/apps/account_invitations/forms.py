from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class AcceptInvitationForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        label="Password",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        label="Confirm Password",
        help_text="Enter the same password as before, for verification.",
    )

    def clean_password(self):
        password = self.cleaned_data["password"]

        validate_password(password)

        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm = cleaned.get("confirm_password")

        if password and confirm and password != confirm:
            raise ValidationError("Passwords do not match.")

        return cleaned
