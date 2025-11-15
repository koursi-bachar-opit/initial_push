from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional


class ListingCreate(BaseModel):
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

    - For normal buyers, buyer_user_id is NOT sent by the frontend; it is
      derived from the authenticated user (get_current_user) on the server.
    - For admin primitives, buyer_user_id can be provided explicitly.
    """
    listing_id: int
    start_time: datetime
    end_time: datetime
    buyer_user_id: Optional[int] = None


class BookingRead(BaseModel):
    """
    Full booking details returned to the frontend.
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

    model_config = ConfigDict(from_attributes=True)