from uuid import UUID
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.bookings.public import get_bookings_public, BookingsPublic

from .repository import OrganizationRepository
from .models import OrgRole
from .schemas import OrganizationCreate, OrganizationUpdate, MembershipCreate, MembershipUpdateRole
from .permissions import OrgPermission


class OrganizationService:
    def __init__(
        self,
        repo: OrganizationRepository,
        bookings_public: BookingsPublic,   #until: for future org-funded bookings
    ):
        self.repo = repo
        self.bookings_public = bookings_public


    def create_organization(self, creator_user_id: UUID, payload: OrganizationCreate):
        """
        Creator becomes the first admin automatically.
        """
        org = self.repo.create(payload.model_dump())

        #creator is automatically an admin
        self.repo.add_member(org.id, creator_user_id, OrgRole.ADMIN)

        return org

    def update_organization(self, org_id: UUID, actor_user_id: UUID, payload: OrganizationUpdate):
        """
        Only organization admins may update org metadata.
        """
        membership = self.repo.get_membership(org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        org = self.repo.get(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        return self.repo.update(org, payload.model_dump(exclude_unset=True))

    #Org membership
    def add_member(self, org_id: UUID, actor_user_id: UUID, user_id: UUID, role: OrgRole):
        """
        Admin adds another member.
        """
        membership = self.repo.get_membership(org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        return self.repo.add_member(org_id, user_id, role)


    def remove_member(self, org_id: UUID, actor_user_id: UUID, user_id: UUID):
        """
        Admin removes a member.
        """
        membership = self.repo.get_membership(org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        return self.repo.remove_member(org_id, user_id)


    def change_member_role(self, org_id: UUID, actor_user_id: UUID, user_id: UUID, role: OrgRole):
        """
        Admin changes another user's role.
        """
        membership = self.repo.get_membership(org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        updated = self.repo.change_role(org_id, user_id, role)
        return updated


    def list_user_organizations(self, user_id: UUID):
        """
        List all orgs a user is a member of.
        """
        return self.repo.list_for_user(user_id)

    def list_members(self, org_id: UUID, requesting_user_id: UUID):
        """
        Only members of an organization can view membership lists.
        """
        membership = self.repo.get_membership(org_id, requesting_user_id)
        OrgPermission.require_member(membership)

        return self.repo.list_members(org_id)

    #helpers exposed in public interface
    def is_org_admin(self, user_id: UUID, org_id: UUID) -> bool:
        """
        Public helper used by other domains (Bookings, Providers, Invoices).
        """
        membership = self.repo.get_membership(org_id, user_id)
        return membership is not None and membership.org_role == OrgRole.ADMIN

    def is_org_member(self, user_id: UUID, org_id: UUID) -> bool:
        membership = self.repo.get_membership(org_id, user_id)
        return membership is not None


def get_organization_service(
    db: Session = Depends(get_db),
    bookings_public: BookingsPublic = Depends(get_bookings_public),
) -> OrganizationService:
    repo = OrganizationRepository(db)
    return OrganizationService(
        repo=repo,
        bookings_public=bookings_public,
    )