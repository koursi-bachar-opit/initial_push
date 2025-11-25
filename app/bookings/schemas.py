from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
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
    For admins only. Buyers should never use this schema. 
    Includes buyer_user_id because admins assign the target buyer explicitly.
    """
    listing_id: UUID
    start_time: datetime
    end_time: datetime
    buyer_user_id: UUID


class BookingRequest(BaseModel):
    """
    Buery booking creation payload.
    """
    listing_id: UUID
    start_time: datetime
    end_time: datetime


class BookingRead(BaseModel):
    """
    Full booking object.
    Includes raw DB fields and conveniece fields for API responses
    """
    id: UUID
    listing_id: UUID
    buyer_user_id: UUID
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