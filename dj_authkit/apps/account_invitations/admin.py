from django.contrib import admin

from .models import AccountInvitation


class AccountInvitationAdmin(admin.ModelAdmin):
    list_display = ["email", "status", "role", "created_at", "token"]
    list_filter = ["status", "role"]


admin.site.register(AccountInvitation, AccountInvitationAdmin)
