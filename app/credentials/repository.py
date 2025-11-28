from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from uuid import UUID

from .models import AccessCredential


class AccessCredentialRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, booking_id, vpn_config_uri, ssh_public_key_fingerprint):
        """"#Create credentials with booking_id as reference information"""
        credential = AccessCredential(
            booking_id=booking_id,
            vpn_config_uri=vpn_config_uri,
            ssh_public_key_fingerprint=ssh_public_key_fingerprint,
        )

        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)

        return credential

    def get_by_booking_id(self, booking_id: UUID):
        stmt = select(AccessCredential).where(
            AccessCredential.booking_id == booking_id
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def mark_revoked(self, credential_id: UUID):
        """
        This marks a credential as revoked by setting a revoked_at timestamp.
        This does not revoke on a provider (for AccessCredentialService).
        """
        stmt = select(AccessCredential).where(AccessCredential.id == credential_id)
        result = self.db.execute(stmt)
        credential = result.scalar_one_or_none()

        if credential is None:
            return None  #service layer decides how to handle "not found"

        credential.revoked_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(credential)

        return credential