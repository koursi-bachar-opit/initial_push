from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional

# Pydantic models for API validation and response serialization

class ListingCreate(BaseModel):
    """Schema for creating a new listing."""
    title: str = Field(min_length=1)
    price: float = Field(ge=0)

class ListingRead(ListingCreate):
    """Schema for reading listing data from DB."""
    id: int
    model_config = ConfigDict(from_attributes=True)

class BookingStatus(str, Enum):
    """Mirror of BookingStatus Enum in models.py for validation."""
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BookingCreate(BaseModel):
    """Schema for creating a booking request."""
    listing_id: int
    buyer_name: str = Field(min_length=1)
    start_time: datetime
    end_time: datetime
    status: BookingStatus = BookingStatus.REQUESTED
    total_price_estimate: Optional[float] = None

class BookingRead(BookingCreate):
    """Schema for returning full booking details."""
    id: int
    active_session_start: Optional[datetime] = None
    active_session_end: Optional[datetime] = None
    actual_price_charged: Optional[float] = None
    usage_seconds: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)