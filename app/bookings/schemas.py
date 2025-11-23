from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

from app.listings.schemas import ListingRead


class BookingStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingAdminCreate(BaseModel):
    """
    For admins. Buyers should never use this schema. 
    Includes buyer_user_id because admins assign the target buyer explicitly.
    """
    listing_id: int
    start_time: datetime
    end_time: datetime
    buyer_user_id: int


class BookingRequest(BaseModel):
    """
    Booking creation payload.
    For normal buyers, buyer_user_id is not sent by the frontend. It is
    currently derived from the authenticated user on the server. (subject to change)
    """
    listing_id: int
    start_time: datetime
    end_time: datetime


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

    """
    Convenience field
    (to generate API responses for now)
    """
    listing_title: Optional[str] = None
    buyer_email: Optional[str] = None

    listing: Optional[ListingRead] = None

    model_config = ConfigDict(from_attributes=True)