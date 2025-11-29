import uuid
from datetime import timedelta
from typing import Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .tokens import generate_invitation_token

User = get_user_model()

INVITE_EXPIRY_HOURS = getattr(
    settings, "DJ_AUTHKIT_ACCOUNT_INVITATION_EXPIRY_HOURS", 24
)


class AccountInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", _("Cancelled")

    email = models.EmailField(unique=False, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    token = models.CharField(max_length=200, unique=True, editable=False, db_index=True)
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_invitations",
    )
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancelled_invitations",
    )

    role = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    # is_accepted = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    invitation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = "Account Invitation"
        verbose_name_plural = "Account Invitations"
        ordering = ("-created_at",)

    def clean(self):
        # Validation logic to ensure either Email OR Phone exists
        if not self.email and not self.phone_number:
            raise ValidationError("You must provide either an email or a phone number.")
        if self.email and self.phone_number:
            raise ValidationError(
                "Please provide only one contact method (Email OR Phone)."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        target = self.email or self.phone_number
        return f"Invite for {target}"

    @classmethod
    def create_invitation(
        cls,
        email: str,
        role: Group,
        invited_by: Union[User, None] = None,
        expiry_hours: int = INVITE_EXPIRY_HOURS,
    ):
        with transaction.atomic():
            # Deactivate existing pending / valid invitations
            cls.expire_active_invitations(email=email)

            # Create the new invitation
            return cls.objects.create(
                email=email,
                role=role,
                token=generate_invitation_token(),
                invited_by=invited_by,
                expires_at=timezone.now() + timedelta(hours=expiry_hours),
            )

    create_invitation.alters_data = True

    @classmethod
    def expire_active_invitations(cls, email: str):
        cls.objects.filter(
            email=email, status=cls.Status.PENDING, expires_at__gt=timezone.now()
        ).update(status=cls.Status.EXPIRED)

    expire_active_invitations.alters_data = True

    @property
    def is_expired(self):
        return self.status == self.Status.EXPIRED or timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Invitation is usable only if not expired and not yet accepted."""

        return self.status == self.Status.PENDING and timezone.now() < self.expires_at

    @property
    def is_accepted(self):
        return self.status == self.Status.ACCEPTED

    def accept(self):
        if self.is_expired:
            raise ValueError("Invitation has expired.")
        if self.is_accepted:
            raise ValueError("Invitation already accepted.")

        self.accepted_at = timezone.now()
        self.status = self.Status.ACCEPTED
        self.save(update_fields=["status", "accepted_at"])

    accept.alters_data = True

    def mark_expired(self):
        self.status = self.Status.EXPIRED
        self.save(update_fields=["status"])

    mark_expired.alters_data = True

    def mark_cancelled(self, cancelled_by: User):
        self.status = self.Status.CANCELLED
        self.cancelled_by = cancelled_by
        self.save(update_fields=["status", "cancelled_by"])

    mark_cancelled.alters_data = True
