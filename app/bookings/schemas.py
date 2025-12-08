from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from enum import Enum

from app.listings.schemas import ListingRead


class BookingStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment" #new status
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
    organization_id: Optional[UUID] = None  #NEW LINE


class BookingRequest(BaseModel):
    """
    Buyer booking creation payload.
    """
    listing_id: UUID
    start_time: datetime
    end_time: datetime
    organization_id: Optional[UUID] = None
    
    @field_validator('start_time', 'end_time', mode='after')
    @classmethod
    def ensure_timezone_aware(cls, v: datetime) -> datetime:
        """Ensure datetime is timezone-aware (assume UTC if naive)"""
        if v.tzinfo is None:
            # Assume UTC if no timezone provided
            return v.replace(tzinfo=timezone.utc)
        return v


# class BookingRequest(BaseModel):
#     """
#     Buery booking creation payload.
#     """
#     listing_id: UUID
#     start_time: datetime
#     end_time: datetime
#     organization_id: Optional[UUID] = None  #NEW LINE


class BookingRead(BaseModel):
    """
    Full booking object.
    Includes raw DB fields and conveniece fields for API responses
    """
    id: UUID
    listing_id: UUID
    buyer_user_id: UUID
    organization_id: Optional[UUID] = None  #NEW LINE
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