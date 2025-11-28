from .service import AccessCredentialService


class AccessCredentialPublic:
    """
    Public API for the credentials domain.
    """
    def __init__(self, service: AccessCredentialService):
        self._service = service

    def issue_for_booking(self, booking):
        return self._service.issue_for_booking(booking)

    def revoke_for_booking(self, booking):
        return self._service.revoke_for_booking(booking)

    def get_for_booking(self, booking_id):
        return self._service.get_for_booking(booking_id)