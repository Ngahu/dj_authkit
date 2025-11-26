from django.urls import path
from .views import AcceptInvitationView


app_name = "account_invitations"

urlpatterns = [
    path(
        "accept/<str:token>/", AcceptInvitationView.as_view(), name="accept_invitation"
    )
]
