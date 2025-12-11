from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    #refactor:
    #hourly_price, daily_price, monthly_price
    price = Column(Float, nullable=False)

    currency = Column(String(length=3), nullable=False, default="USD")

    #refactor:
    #availability_status
    #cancellation_policy

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False)

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    benchmarks = relationship(
        "MachineBenchmark", 
        back_populates="listing",
        cascade="all, delete-orphan"
    )
    
    machine = relationship("Machine", back_populates="listings")
    bookings = relationship("Booking", back_populates="listing", cascade="all, delete")