from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

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

    id = Column(Integer, primary_key=True, index=True)

    #Link buyer_user_id to buyer's account creds
    buyer_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    listing_id = Column(
        Integer,
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
    )

    #Booking window
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    total_price_estimate = Column(Float, nullable=False)

    #Enum value stored as VARCHAR data
    status = Column(
        SQLEnum(BookingStatus, name="bookingstatus", native_enum=False),
        nullable=False,
        default=BookingStatus.REQUESTED,
    )

    #Relationships
    listing = relationship("Listing", back_populates="bookings")
    buyer = relationship("User")

    active_session_start = Column(DateTime(timezone=True), nullable=True)
    active_session_end = Column(DateTime(timezone=True), nullable=True)
    actual_price_charged = Column(Float, nullable=True)
    usage_seconds = Column(Float, nullable=True)


    """
    Additional temporary computed fields for API responses 
    """
    @property
    def listing_title(self):
        return self.listing.title if self.listing else None

    @property
    def buyer_email(self):
        return self.buyer.email if self.buyer else None