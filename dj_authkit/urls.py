from django.urls import include, path


app_name = "dj_authkit"


urlpatterns = [
    path(
        "account-invitations/",
        include(
            "dj_authkit.apps.account_invitations.urls", namespace="account_invitations"
        ),
    ),
]
