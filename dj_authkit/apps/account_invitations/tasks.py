from __future__ import absolute_import, unicode_literals
import structlog
from celery import shared_task
from dj_authkit.apps.account_invitations.services import AccountInvitationService
from dj_authkit.apps.account_invitations.models import AccountInvitation

logger = structlog.get_logger()


@shared_task(
    name="dj_authkit.apps.account_invitations.tasks.cleanup_expired_invitations",
    bind=True,
)
def cleanup_expired_invitations(self):
    try:
        AccountInvitationService.cleanup_expired_invitations()

    except Exception as er:
        logger.warning("cleanup_expired_invitations.error", error=er)


@shared_task(
    name="dj_authkit.apps.account_invitations.tasks.send_invitation_notification",
    bind=True,
)
def send_invitation_notification(self, invitation_id: str, site_url: str):
    try:
        invite = AccountInvitation.objects.get(invitation_id=invitation_id)

    except Exception as er:
        logger.warning("send_invitation_notification.error", error=er)
