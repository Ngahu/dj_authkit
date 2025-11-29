from dataclasses import dataclass
from typing import Dict, Optional

import structlog
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from dj_authkit.apps.account_invitations.models import AccountInvitation

from .exceptions import (
    InvitationAlreadyAcceptedError,
    InvitationExpiredError,
    InvitationNotFoundError,
)

User = get_user_model()
logger = structlog.get_logger()


@dataclass
class AccountInvitationService:
    """
    Service layer for all invitation operations:
        - create invitation
        - send invitation email
        - accept invitation
        - cleanup expired invitations

    No invitation logic is duplicated here — creation is delegated to the model.
    """

    email_sender: str = settings.DEFAULT_FROM_EMAIL
    accept_url_name: str = "dj_authkit:account_invitations:accept_invitation"

    @staticmethod
    def create_invitation(*, email: str, role, invited_by=None, expiry_hours: int = 24):
        """
        Delegates to AccountInvitation.create_invitation()
        """
        return AccountInvitation.create_invitation(
            email=email,
            role=role,
            invited_by=invited_by,
            expiry_hours=expiry_hours,
        )

    @classmethod
    @transaction.atomic
    def accept_invitation(
        cls,
        *,
        token: str,
        password: str,
        extra_user_fields: Optional[Dict] = None,
    ) -> User:
        """
        Accept an invitation, create user, assign role, mark accepted.
        """
        if extra_user_fields is None:
            extra_user_fields = {}

        extra_user_fields.setdefault("is_active", True)
        extra_user_fields.setdefault("user_type", User.UserTypesChoices.STAFF)

        invitation = cls._get_invitation(token)
        cls._validate_invitation(invitation)

        # Create the user
        user = User.objects.create_user(
            email=invitation.email,
            password=password,
            **extra_user_fields,
        )

        # Assign the role (django.contrib.auth Group)
        if invitation.role:
            invitation.role.user_set.add(user)

        invitation.accept()
        return user

    @staticmethod
    def cleanup_expired_invitations() -> int:
        """
        Marks all expired pending invitations as EXPIRED and deletes EXPIRED invitations.
        Returns number updated.
        """
        now = timezone.now()

        qs = AccountInvitation.objects.filter(
            status=AccountInvitation.Status.PENDING,
            expires_at__lt=now,
        )
        count = qs.update(status=AccountInvitation.Status.EXPIRED)

        logger.info(f"expired_invitations count is {count}")

        to_delete = AccountInvitation.objects.filter(
            status=AccountInvitation.Status.EXPIRED
        )
        logger.info(f"expired_invitations to_delete count is {to_delete.count()}")

        to_delete.delete()

        return True

    def send_invitation_email(self, *, invitation: AccountInvitation, site_url: str):
        """
        Sends the invitation email to the invited user.
        """
        accept_url = reverse(self.accept_url_name, kwargs={"token": invitation.token})

        accept_link = site_url + accept_url

        message = (
            f"You've been invited to create an account with role '{invitation.role.name}'.\n\n"
            f"Click the link below to accept the invitation:\n"
            f"{accept_link}\n\n"
            f"This link expires on {invitation.expires_at}."
        )

        send_mail(
            subject="You're Invited!",
            message=message,
            from_email=self.email_sender,
            recipient_list=[invitation.email],
        )

    @staticmethod
    def _get_invitation(token: str) -> AccountInvitation:
        try:
            return AccountInvitation.objects.get(token=token)
        except AccountInvitation.DoesNotExist:
            raise InvitationNotFoundError("Invitation not found.")

    @staticmethod
    def _validate_invitation(invitation: AccountInvitation):
        if invitation.is_expired:
            raise InvitationExpiredError("Invitation has expired.")

        if invitation.is_accepted:
            raise InvitationAlreadyAcceptedError("Invitation already accepted.")
