import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.database import Base


class WipeReviewStatus(PyEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class WipeAttestation(Base):
    __tablename__ = "wipe_attestations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  #1 -> 1 Booking→Attestation
    )

    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
    )

    method = Column(String, nullable=False)
    evidence_uri = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    attested_at = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(
        Enum(WipeReviewStatus), default=WipeReviewStatus.PENDING, nullable=False
    )