from fastapi import Depends
from app.database import get_db

from datetime import datetime

from .repository import AccessCredentialRepository
from .issuer import CredentialIssuer

from .issuer import get_credential_issuer

from uuid import UUID


class AccessCredentialService:
    def __init__(
        self,
        repo: AccessCredentialRepository,
        issuer: CredentialIssuer,
        
    ):
        self.repo = repo
        self.issuer = issuer


    def issue_for_booking(self, booking):
        """
        Issues credentials for a booking, but only if the booking is ACTIVE.
        """

        #Gather related objects
        user = booking.buyer
        machine = booking.listing.machine

        #Issue via issuer strategy
        payload = self.issuer.issue(
            booking=booking,
            user=user,
            machine=machine,
        )

        # 4. Persist
        return self.repo.create(
            booking_id=booking.id,
            vpn_config_uri=payload.vpn_config_uri,
            ssh_public_key_fingerprint=payload.ssh_public_key_fingerprint,
        )


    def revoke_for_booking(self, booking):
        """
        Revoke credentials for a booking.
        """
        credentials = self.repo.get_by_booking_id(booking.id)

        if not credentials:
            return []
        
        revoked_list = []

        for credential in credentials:
            self.issuer.revoke(credential)
            updated = self.repo.mark_revoked(credential.id)
            revoked_list.append(updated)

        return revoked_list


    def get_for_booking(self, booking):
        """
        Return credentials for displaying or auditing.
        """
        return self.repo.get_by_booking_id(booking.id)


def get_access_credential_service(
    db = Depends(get_db),
    issuer: CredentialIssuer = Depends(get_credential_issuer),
) -> AccessCredentialService:

    repo = AccessCredentialRepository(db)

    return AccessCredentialService(
        repo=repo,
        issuer=issuer,
    )