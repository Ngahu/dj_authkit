# Use 'alpha', 'beta', 'rc' or 'final' as the 4th element to indicate release type.

__version_info__ = {
    "major": 0,
    "minor": 8,
    "micro": 0,
    "releaselevel": "rc",
    "serial": 1,
}


def get_version(short=False):
    """
    Return the latest version of the project.
    """
    assert __version_info__["releaselevel"] in ("alpha", "beta", "rc", "final")
    vers = [
        "%(major)i.%(minor)i" % __version_info__,
    ]
    if __version_info__["micro"]:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__["releaselevel"] != "final" and not short:
        vers.append(
            "%s%i" % (__version_info__["releaselevel"][0], __version_info__["serial"])
        )
    return "".join(vers)


DJ_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.staticfiles",
]


AUTHKIT_APPS = [
    "dj_authkit.config.DjAuthkit",
    "dj_authkit.apps.accounts",
    "dj_authkit.apps.account_invitations",
]


THIRDPARY_APPS = []


DJ_AUTHKIT_APPS = [*AUTHKIT_APPS, *THIRDPARY_APPS]

INSTALLED_APPS = [*DJ_APPS, *DJ_AUTHKIT_APPS]


DJ_AUTHKIT_AUTH_USER_MODEL = "accounts.User"

DJ_AUTHKIT_ACCOUNT_INVITATION_EXPIRY_HOURS = 24
