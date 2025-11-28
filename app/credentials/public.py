from typing import Protocol
from uuid import UUID
from fastapi import Depends
from app.database import get_db
from sqlalchemy.orm import Session

from .service import AccessCredentialService, get_access_credential_service


class AccessCredentialsPublic(Protocol):
    """
    Public interface exposed by the Credentials domain.
    """
    def issue_for_booking(self, booking):
        ...

    def revoke_for_booking(self, booking):
        ...

    def get_for_booking(self, booking):
        ...


class AccessCredentialsPublicImpl:
    """
    Concrete adapter around AccessCredentialService.
    """
    def __init__(self, svc: AccessCredentialService):
        self.svc = svc

    def issue_for_booking(self, booking):
        return self.svc.issue_for_booking(booking)

    def revoke_for_booking(self, booking):
        return self.svc.revoke_for_booking(booking)

    def get_for_booking(self, booking):
        return self.svc.get_for_booking(booking)


def get_credentials_public(
    svc: AccessCredentialService = Depends(get_access_credential_service)
) -> AccessCredentialsPublic:
    return AccessCredentialsPublicImpl(svc)