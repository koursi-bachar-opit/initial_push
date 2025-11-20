from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum

#An enum representation provides safe booking states
class BookingStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    BUYER = "buyer"
    PROVIDER = "provider"
    ADMIN = "admin"
    ORG_ADMIN = "org_admin"

class User(Base):
    """
    Types of users on the marketplace
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    supabase_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(SQLEnum(UserRole, native_enum=False), nullable=False, default=UserRole.BUYER)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # A provider can own many machines
    machines = relationship("Machine", back_populates="provider")

class Machine(Base):
    """
    These are the physical servers offered by providers.
    Most hardware attributes are nullable until full buildout.
    """
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)

    # Link to the provider's user account
    provider_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Hardware / location attributes (nullable for now)
    hostname = Column(String, nullable=True)
    location_region = Column(String, nullable=True)
    gpu_model = Column(String, nullable=True)
    gpu_count = Column(Integer, nullable=True)
    vram_gb = Column(Integer, nullable=True)
    cpu_model = Column(String, nullable=True)
    cpu_cores = Column(Integer, nullable=True)
    ram_gb = Column(Integer, nullable=True)
    storage_gb = Column(Integer, nullable=True)
    network_mbps = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    provider = relationship("User", back_populates="machines")
    listings = relationship("Listing", back_populates="machine")

class Listing(Base):
    """
    A listing is something a provider offers for rent.
    For example, a VM, GPU instance, or small compute server.
    Buyers can browse listings and book them for a time window.
    """
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)

    #The listing links to the underlying machine being rented
    machine_id = Column(
        Integer,
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
    )

    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    #Listing has cardinal relationships to machine and bookings
    machine = relationship("Machine", back_populates="listings")
    bookings = relationship("Booking", back_populates="listing")


class Booking(Base):
    """
    Represents a booking event requested by a buyer
    for a specific provier listing. Exists in multiple
    status states.
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

    #Runtime usage details
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