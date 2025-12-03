from typing import Protocol, List
from uuid import UUID

from fastapi import Depends, HTTPException, status  #HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db

from .service import OrganizationService, get_organization_service
from .models import Organization, OrganizationMembership

#

from app.auth.auth import get_current_user


class OrganizationsPublic(Protocol):
    """
    Public interface for interacting with the Organizations domain.
    """
    def get_organization(self, org_id: UUID) -> Organization | None:
        ...

    def is_org_admin(self, user_id: UUID, org_id: UUID) -> bool:
        ...

    def is_org_member(self, user_id: UUID, org_id: UUID) -> bool:
        ...

    def list_user_organizations(self, user_id: UUID) -> List[Organization]:
        ...

    def get_membership(
        self, org_id: UUID, user_id: UUID
    ) -> OrganizationMembership | None:
        ...

    #refactor: move to permissions (without circular import)
    def require_org_member_or_admin(
        self,
        org_id: UUID,
        current_user=Depends(get_current_user),
    ) -> bool:
        ...


class OrganizationsPublicImpl(OrganizationsPublic):

    def __init__(self, service: OrganizationService):
        self.service = service

    #Orgs
    def get_organization(self, org_id: UUID):
        return self.service.repo.get(org_id)

    #Permission helpers
    def is_org_admin(self, user_id: UUID, org_id: UUID) -> bool:
        return self.service.is_org_admin(user_id, org_id)

    def is_org_member(self, user_id: UUID, org_id: UUID) -> bool:
        return self.service.is_org_member(user_id, org_id)

    #User's org list
    def list_user_organizations(self, user_id: UUID):
        return self.service.list_user_organizations(user_id)

    #Membership lookup
    def get_membership(self, org_id: UUID, user_id: UUID):
        return self.service.repo.get_membership(org_id, user_id)
    
    #refactor: move to permissions (without circular import)
    def require_org_member_or_admin(
        self,
        org_id: UUID,
        current_user=Depends(get_current_user),
    ):
        if not self.is_org_member(current_user.id, org_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization.",
            )
        return True


def get_organizations_public(
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationsPublic:
    return OrganizationsPublicImpl(service)