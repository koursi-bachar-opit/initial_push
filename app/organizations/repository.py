from sqlalchemy.orm import Session
from uuid import UUID

from .models import Organization, OrganizationMembership, OrgRole

class OrganizationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Organization:
        org = Organization(**data)
        self.db.add(org)
        self.db.commit()
        self.db.refresh(org)
        return org

    def update(self, org: Organization, data: dict) -> Organization:
        for k, v in data.items():
            setattr(org, k, v)
        self.db.commit()
        self.db.refresh(org)
        return org

    def get(self, org_id: UUID) -> Organization | None:
        return self.db.query(Organization).filter_by(id=org_id).first()

    def list_for_user(self, user_id: UUID):
        return (
            self.db.query(Organization)
            .join(OrganizationMembership)
            .filter(OrganizationMembership.user_id == user_id)
            .all()
        )

    #memberships
    def add_member(self, org_id: UUID, user_id: UUID, role: OrgRole):
        record = OrganizationMembership(
            organization_id=org_id,
            user_id=user_id,
            org_role=role,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def remove_member(self, org_id: UUID, user_id: UUID):
        self.db.query(OrganizationMembership).filter_by(
            organization_id=org_id,
            user_id=user_id
        ).delete()
        self.db.commit()

    def change_role(self, org_id: UUID, user_id: UUID, role: OrgRole):
        membership = (
            self.db.query(OrganizationMembership)
            .filter_by(organization_id=org_id, user_id=user_id)
            .first()
        )
        membership.org_role = role
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def list_members(self, org_id: UUID):
        return (
            self.db.query(OrganizationMembership)
            .filter_by(organization_id=org_id)
            .all()
        )

    def get_membership(self, org_id: UUID, user_id: UUID):
        return (
            self.db.query(OrganizationMembership)
            .filter_by(organization_id=org_id, user_id=user_id)
            .first()
        )