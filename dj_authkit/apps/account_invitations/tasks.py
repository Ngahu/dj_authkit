from __future__ import absolute_import, unicode_literals
import structlog
from celery import shared_task
from dj_authkit.apps.account_invitations.services import AccountInvitationService

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
