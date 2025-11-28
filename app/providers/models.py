import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


# Enums
class ProviderVerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class VerificationSubject(str, enum.Enum):
    provider = "provider"
    machine = "machine"


class ProviderProfile(Base):
    __tablename__ = "provider_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    #A User may have 0 or 1 provider profile
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    verification_status = Column(
        Enum(ProviderVerificationStatus, name="provider_verification_status"),
        default=ProviderVerificationStatus.PENDING,
        nullable=False,
    )

    payout_account_ref = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    #provider or machine
    subject_type = Column(
        Enum(VerificationSubject, name="verification_subject"),
        nullable=False,
    )

    #ID of provider_profile.id or machine.id (not FK)
    subject_id = Column(UUID(as_uuid=True), nullable=False)

    status = Column(
        Enum(VerificationStatus, name="verification_status"),
        default=VerificationStatus.PENDING,
        nullable=False,
    )

    #User performing the verification (admin)
    performed_by_admin_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    notes = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )