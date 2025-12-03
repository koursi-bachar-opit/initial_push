import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    FINALIZED = "finalized"
    PAID = "paid"
    VOID = "void"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)

    total_amount = Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=0,
    )

    currency = Column(String(length=3), nullable=False, default="usd")

    status = Column(
        Enum(InvoiceStatus, name="invoice_status"),
        nullable=False,
        default=InvoiceStatus.PENDING,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    #model check
    def is_modifiable(self) -> bool:
        """Invoices are immutable once finalized; only VOID allowed via service rules."""
        return self.status in {InvoiceStatus.PENDING}