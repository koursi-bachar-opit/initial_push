from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional


class ListingCreate(BaseModel):
    """Payload sent by providers or admins when creating a new listing."""
    title: str = Field(min_length=1)
    price: float = Field(ge=0)


class ListingRead(ListingCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BookingStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingCreate(BaseModel):
    """
    Booking creation payload.
    For normal buyers, buyer_user_id is not sent by the frontend. It is
    currently derived from the authenticated user on the server. (subject to change)
    For admin primitives, buyer_user_id can be provided explicitly.
    """
    listing_id: int
    start_time: datetime
    end_time: datetime
    buyer_user_id: Optional[int] = None


class BookingRead(BaseModel):
    """
    This is the full booking object.
    Includes raw DB fields and conveniece fields
    """
    id: int
    listing_id: int
    buyer_user_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    total_price_estimate: Optional[float] = None
    active_session_start: Optional[datetime] = None
    active_session_end: Optional[datetime] = None
    actual_price_charged: Optional[float] = None
    usage_seconds: Optional[float] = None

    """API responses for now"""
    listing_title: Optional[str] = None
    buyer_email: Optional[str] = None


    model_config = ConfigDict(from_attributes=True)