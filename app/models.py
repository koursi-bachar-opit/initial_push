from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum

# Enum representing allowed booking states
class BookingStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Listing(Base):
    """Represents a rentable compute resource or server."""
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    # One-to-many relationship with bookings
    bookings = relationship("Booking", back_populates="listing")


class Booking(Base):
    """Represents a booking event made by a buyer for a specific listing."""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    # Link to the buyer user account
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

    # Booking window
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    total_price_estimate = Column(Float, nullable=False)

    # Enum value stored as VARCHAR (non-native)
    status = Column(
        SQLEnum(BookingStatus, name="bookingstatus", native_enum=False),
        nullable=False,
        default=BookingStatus.REQUESTED,
    )

    # Relationships
    listing = relationship("Listing", back_populates="bookings")
    buyer = relationship("User")

    # Runtime usage details
    active_session_start = Column(DateTime(timezone=True), nullable=True)
    active_session_end = Column(DateTime(timezone=True), nullable=True)
    actual_price_charged = Column(Float, nullable=True)
    usage_seconds = Column(Float, nullable=True)


class UserRole(str, Enum):
    BUYER = "buyer"
    PROVIDER = "provider"
    ADMIN = "admin"
    ORG_ADMIN = "org_admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    supabase_id = Column(String, unique=True, index=True, nullable=False)  # sub from JWT
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(SQLEnum(UserRole, native_enum=False), nullable=False, default=UserRole.BUYER)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)