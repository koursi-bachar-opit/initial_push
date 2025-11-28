import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from app.database import Base


class DisputeStatus(str, enum.Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    NEEDS_INFO = "needs_info"
    RESOLVED_REFUNDED = "resolved_refunded"
    RESOLVED_DENIED = "resolved_denied"
    CLOSED = "closed"


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
    )

    opened_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )

    reason = Column(Text, nullable=False)

    status = Column(
        Enum(DisputeStatus, name="dispute_status"),
        nullable=False,
        default=DisputeStatus.OPEN,
    )

    resolution_notes = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    #repr/debug helpers
    def __repr__(self) -> str:
        return (
            f"<Dispute id={self.id} booking_id={self.booking_id} "
            f"status={self.status}>"
        )