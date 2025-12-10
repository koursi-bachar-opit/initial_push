import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from enum import Enum as PyEnum


class OrganizationStatus(str, PyEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class OrgRole(str, PyEnum):
    ADMIN = "admin"
    MEMBER = "member"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    billing_email = Column(String, nullable=False)
    status = Column(Enum(OrganizationStatus), default=OrganizationStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))

    memberships = relationship("OrganizationMembership", back_populates="organization")

    bookings = relationship("Booking", back_populates="organization")


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    org_role = Column(Enum(OrgRole), default=OrgRole.MEMBER)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", back_populates="organization_memberships")