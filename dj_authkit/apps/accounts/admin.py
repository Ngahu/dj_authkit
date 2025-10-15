from django.contrib import admin


from django.contrib.auth.admin import UserAdmin

from django.contrib.auth import get_user_model

from .forms import CustomUserChangeForm, CustomUserCreationForm

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = (
        "email",
        "user_type",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active", "user_type", "registration_medium")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "phone_number",
                    "first_name",
                    "last_name",
                    "user_type",
                    "password",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone_number",
                    "user_type",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)
