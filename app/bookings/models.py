from sqlalchemy import Column, Float, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum
import uuid

from app.database import Base


class BookingStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base):
    """
    Buyer booking a listing for a specific time window.
    """
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    #Link buyer_user_id to buyer's account creds
    buyer_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    listing_id = Column(
        UUID(as_uuid=True),
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    organization_id = Column(  #NEW LINE
        UUID(as_uuid=True),  #NEW LINE
        ForeignKey("organizations.id", ondelete="SET NULL"),  #NEW LINE
        nullable=True,  #NEW LINE
        index=True,  #NEW LINE
    )  #NEW LINE

    #Booking window
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    #Pricing
    total_price_estimate = Column(Float, nullable=False)
    actual_price_charged = Column(Float, nullable=True)
    usage_seconds = Column(Float, nullable=True)

    #Enum value stored as VARCHAR data
    status = Column(
        SQLEnum(BookingStatus, name="bookingstatus", native_enum=False),
        nullable=False,
        default=BookingStatus.REQUESTED,
    )

    #Session window for active state
    active_session_start = Column(DateTime(timezone=True), nullable=True)
    active_session_end = Column(DateTime(timezone=True), nullable=True)

    #Relationships
    listing = relationship("Listing", back_populates="bookings")
    buyer = relationship("User")

    access_credentials = relationship(
        "AccessCredential",
        back_populates="booking",
        cascade="all, delete-orphan"
    )


    """
    Additional temporary computed fields for API responses 
    """
    @property
    def listing_title(self):
        return self.listing.title if self.listing else None

    @property
    def buyer_email(self):
        return self.buyer.email if self.buyer else None