import hashlib
import importlib
import uuid

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, Group, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from dj_authkit.apps.accounts.managers import UserManager

if apps.is_installed("rest_framework.authtoken"):
    try:
        Token = importlib.import_module("rest_framework.authtoken.models").Token

        @receiver(post_save, sender=settings.AUTH_USER_MODEL)
        def create_auth_token(sender, instance=None, created=False, **kwargs):
            if created:
                Token.objects.create(user=instance)

    except ImportError:
        pass


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Email and password are required. Other fields are optional.
    """

    username = None
    email = models.EmailField(
        db_index=True,
        verbose_name="Email Address",
        max_length=255,
        unique=True,
    )
    phone_number = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Phone Number",
        unique=True,
        blank=True,
        null=True,
    )

    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(
        max_length=150, verbose_name="First Name", blank=True, null=True
    )
    last_name = models.CharField(
        max_length=150, verbose_name="Last Name", blank=True, null=True
    )

    class RegistrationMediumChoices(models.TextChoices):
        EMAIL = "Email", _("Email- User registered using their email address.")
        PHONE_NUMBER = (
            "Phone Number",
            _("Phone Number- User registered using their phone number."),
        )

    registration_medium = models.CharField(
        max_length=20,
        choices=RegistrationMediumChoices.choices,
        default=RegistrationMediumChoices.EMAIL,
    )

    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    timestamp = models.DateTimeField(
        _("Date Registered"), auto_now_add=True, db_index=True
    )
    last_updated_at = models.DateTimeField(
        _("Date updated"), auto_now=True, db_index=True
    )

    class UserTypesChoices(models.TextChoices):
        OWNER = "Owner", _("Owner")
        STAFF = "Staff", _("Staff")
        CUSTOMER = "Customer", _("Customer")

    user_type = models.CharField(
        _("User Type"),
        max_length=50,
        choices=UserTypesChoices.choices,
        default=UserTypesChoices.CUSTOMER,
    )

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        constraints = [
            models.UniqueConstraint(
                fields=["phone_number", "email"], name="unique_phone_number_and_email"
            )
        ]

    def __str__(self):
        return self.get_email

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def get_full_name(self):
        if self.first_name and self.last_name:
            full_name = "%s %s" % (self.first_name, self.last_name)
            return full_name.strip()

        elif self.first_name:
            full_name = "%s" % (self.first_name)
            return full_name.strip()

        elif self.last_name:
            full_name = "%s" % (self.last_name)
            return full_name.strip()

        else:
            return self.get_short_name

    @property
    def get_email(self) -> str | None:
        return self.email

    @property
    def get_phone_number(self) -> str | None:
        return self.phone_number

    @property
    def registered_using_email(self) -> bool:
        return self.registration_medium == self.RegistrationMediumChoices.EMAIL

    @property
    def registered_using_phone_number(self) -> bool:
        return self.registration_medium == self.RegistrationMediumChoices.PHONE_NUMBER

    @property
    def is_owner(self):
        return self.user_type == self.UserTypesChoices.OWNER

    @property
    def is_staff_user(self):
        return self.user_type == self.UserTypesChoices.STAFF

    @property
    def is_customer(self):
        return self.user_type == self.UserTypesChoices.CUSTOMER

    @property
    def get_short_name(self):
        # The user is identified by their email or phone number
        return self.get_email or self.get_phone_number

    def has_perm(self, perm, obj=None):
        # Does the user have a specific permission?
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def get_user_id(self):
        return self.user_id

    @property
    def is_admin(self):
        return self.admin

    @cached_property
    def get_roles_with_color(self):
        """
        Returns a list of dicts:
        [
            {"name": "Admin", "color": "#a1b2c3"},
            {"name": "Editor", "color": "#d4e5f6"},
            ...
        ]
        Color is a hex string deterministically generated from the role name.
        """

        def get_color_for_role(role_name):
            # Hash the role name to an integer
            h = hashlib.md5(role_name.encode()).hexdigest()
            # Use first 6 chars of hash as hex color code
            return f"#{h[:6]}"

        colored_roles = []
        for group in self.groups.all():
            color = get_color_for_role(group.name)
            colored_roles.append(
                {
                    "name": group.name,
                    "color": color,
                }
            )

        return colored_roles

    def activate(self):
        self.is_active = True
        self.save()

    activate.alters_data = True


class GroupProfile(models.Model):
    group = models.OneToOneField(
        Group, on_delete=models.CASCADE, related_name="profile", primary_key=True
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.group.name}"
