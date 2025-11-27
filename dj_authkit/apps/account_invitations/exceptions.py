class InvitationError(Exception):
    """Base exception for invitation failures."""


class InvitationExpiredError(InvitationError):
    pass


class InvitationAlreadyAcceptedError(InvitationError):
    pass


class InvitationNotFoundError(InvitationError):
    pass
