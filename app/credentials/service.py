from fastapi import Depends
from app.database import get_db

from datetime import datetime

from .repository import AccessCredentialRepository
from .issuer import CredentialIssuer

from app.bookings.public import BookingsPublic, get_bookings_public
from .issuer import get_credential_issuer

from uuid import UUID


class AccessCredentialService:
    def __init__(
        self,
        repo: AccessCredentialRepository,
        issuer: CredentialIssuer,
        bookings_public: BookingsPublic,
    ):
        self.repo = repo
        self.issuer = issuer
        self.bookings_public = bookings_public


    def issue_for_booking(self, booking_id: UUID):
        """
        Issues credentials for a booking, but only if the booking is ACTIVE.
        """
        booking = self.bookings_public.get_booking(booking_id)

        #Use the public interface to check lifecycle state
        if not self.bookings_public.is_active(booking):
            raise ValueError("Cannot issue credentials unless booking is ACTIVE")

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


    def revoke_for_booking(self, booking_id: UUID):
        """
        Revoke credentials for a booking.
        """
        booking = self.bookings_public.get_booking(booking_id)
        
        credentials = self.repo.get_by_booking_id(booking.id)

        if not (self.bookings_public.is_cancelled(booking) or self.bookings_public.is_completed(booking)):
            raise ValueError("Booking must be cancelled or completed in order to revoke")

        if not credentials:
            return []
        
        revoked_list = []

        for credential in credentials:
            self.issuer.revoke(credential)
            updated = self.repo.mark_revoked(credential.id)
            revoked_list.append(updated)

        return revoked_list


    def get_for_booking(self, booking_id):
        """
        Return credentials for displaying or auditing.
        """
        booking = self.bookings_public.get_booking(booking_id)
        if not self.bookings_public.is_active(booking):
            return []
        return self.repo.get_by_booking_id(booking_id)


def get_access_credential_service(
    db = Depends(get_db),
    bookings_public: BookingsPublic = Depends(get_bookings_public),
    issuer: CredentialIssuer = Depends(get_credential_issuer),
) -> AccessCredentialService:

    repo = AccessCredentialRepository(db)

    return AccessCredentialService(
        repo=repo,
        issuer=issuer,
        bookings_public=bookings_public,
    )