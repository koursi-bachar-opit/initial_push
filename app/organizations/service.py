from uuid import UUID
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db

from .repository import OrganizationRepository
from .models import OrgRole
from .schemas import OrganizationCreate, OrganizationUpdate, MembershipCreate, MembershipUpdateRole
from .permissions import OrgPermission


class OrganizationService:
    def __init__(
        self,
        db: Session,
        repo: OrganizationRepository,
    ):
        self.db = db
        self.repo = repo


    def create_organization(self, creator_user_id: UUID, payload: OrganizationCreate):
        """
        Creator becomes the first admin automatically.
        """
        org = self.repo.create(self.db, payload.model_dump())

        #creator is automatically an admin
        self.repo.add_member(self.db, org.id, creator_user_id, OrgRole.ADMIN)

        return org

    def update_organization(self, org_id: UUID, actor_user_id: UUID, payload: OrganizationUpdate):
        """
        Only organization admins may update org metadata.
        """
        membership = self.repo.get_membership(self.db, org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        org = self.repo.get(self.db, org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        return self.repo.update(self.db, org, payload.model_dump(exclude_unset=True))

    #Org membership
    def add_member(self, org_id: UUID, actor_user_id: UUID, user_id: UUID, role: OrgRole):
        """
        Admin adds another member.
        """
        membership = self.repo.get_membership(self.db, org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        return self.repo.add_member(self.db, org_id, user_id, role)


    def remove_member(self, org_id: UUID, actor_user_id: UUID, user_id: UUID):
        """
        Admin removes a member.
        """
        membership = self.repo.get_membership(self.db, org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        return self.repo.remove_member(self.db, org_id, user_id)


    def change_member_role(self, org_id: UUID, actor_user_id: UUID, user_id: UUID, role: OrgRole):
        """
        Admin changes another user's role.
        """
        membership = self.repo.get_membership(self.db, org_id, actor_user_id)
        OrgPermission.require_admin(membership)

        updated = self.repo.change_role(self.db, org_id, user_id, role)
        return updated


    def list_user_organizations(self, user_id: UUID):
        """
        List all orgs a user is a member of.
        """
        return self.repo.list_for_user(self.db, user_id)

    def list_members(self, org_id: UUID, requesting_user_id: UUID):
        """
        Only members of an organization can view membership lists.
        """
        membership = self.repo.get_membership(self.db, org_id, requesting_user_id)
        OrgPermission.require_member(membership)

        return self.repo.list_members(self.db, org_id)

    #helpers exposed in public interface
    def is_org_admin(self, user_id: UUID, org_id: UUID) -> bool:
        """
        Public helper used by other domains (Bookings, Providers, Invoices).
        """
        membership = self.repo.get_membership(self.db, org_id, user_id)
        return membership is not None and membership.org_role == OrgRole.ADMIN

    def is_org_member(self, user_id: UUID, org_id: UUID) -> bool:
        membership = self.repo.get_membership(self.db, org_id, user_id)
        return membership is not None


def get_organization_service(
    db: Session = Depends(get_db),
) -> OrganizationService:
    repo = OrganizationRepository()
    return OrganizationService(
        db=db,
        repo=repo,
    )