from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String, text
import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from app.database import Base


#Enums
class PaymentType(str, enum.Enum):
    ESCROW = "escrow"
    CAPTURE = "capture"
    REFUND = "refund"


class PaymentStatus(str, enum.Enum):
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    REFUNDED = "refunded"
    FAILED = "failed"
    CANCELLED = "cancelled"


#Payment model
class Payment(Base):
    """
    Payment domain model.

    Reflects the Payment entity from the domain diagram:
    - belongs to a Booking
    - created during escrow, capture, or refund
    - immutable after creation except status updates
    """
    __tablename__ = "payments"

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
        index=True,
    )

    #Domain fields
    type = Column(
        Enum(PaymentType, name="payment_type_enum"),
        nullable=False,
    )

    processor_ref = Column(
        String,
        nullable=False,
        doc="Reference returned by the payment processor (e.g., Stripe PaymentIntent ID)",
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False,
        doc="The amount associated with this payment operation",
    )

    currency = Column(
        String,
        nullable=False,
        default="USD",
    )

    status = Column(
        Enum(PaymentStatus, name="payment_status_enum"),
        nullable=False,
        default=PaymentStatus.AUTHORIZED,
    )

    created_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    #repr/debug helpers
    def __repr__(self) -> str:
        return (
            f"<Payment id={self.id} type={self.type} booking={self.booking_id} "
            f"amount={self.amount} status={self.status}>"
        )