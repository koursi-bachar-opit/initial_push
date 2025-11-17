from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import models, schemas

"""
Repository methods for interacting with Booking objects.
This layer handles direct DB reads/writes and lightweight validation.
State transitions happen in bookings_service.py.
"""

def create_booking(db: Session, data: schemas.BookingCreate) -> models.Booking:
    """
    This is the low-level primitive used by the service layer to create a booking.
    It assumes the caller manages the booking process (separation of concerns),
    and it performs curcial validation:
    1. A listing must exist
    2. The time window must be valid
    3. Necessitates a buyer id
    It also computes the estimated price based on whole hours.
    """
    listing = db.get(models.Listing, data.listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if data.end_time <= data.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    if data.buyer_user_id is None:
        raise HTTPException(
            status_code=400,
            detail="buyer_user_id is required for admin booking creation",
        )

    #Compute the duration in hours.
    #A booking is charged in whole hours, so times are rounded up in hour.
    delta: timedelta = data.end_time - data.start_time
    hours = (delta.total_seconds() + 3599) // 3600
    total = int(hours) * int(listing.price)

    b = models.Booking(
        listing_id=listing.id,
        buyer_user_id=data.buyer_user_id,
        start_time=data.start_time,
        end_time=data.end_time,
        status=models.BookingStatus.REQUESTED,
        total_price_estimate=total,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def list_bookings(db: Session):
    """
    Return every booking in the system. 
    The router/service layer ensures only 
    admins or providers can call this.
    Should be refactored to consider provider access limitations.
    """
    return (
        db.query(models.Booking)
        .order_by(models.Booking.id.asc())
        .all()
    )


def list_bookings_for_user(db: Session, user_id: int):
    """Buyers only see their own bookings, filtered by buyer_user_id."""
    return (
        db.query(models.Booking)
        .filter(models.Booking.buyer_user_id == user_id)
        .order_by(models.Booking.id.asc())
        .all()
    )


def list_bookings_for_provider(db: Session, provider_id: int):
    """
    Providers only see the bookings that have been made on their machines.
    """
    return (
        db.query(models.Booking)
        .join(models.Listing, models.Booking.listing_id == models.Listing.id)
        .join(models.Machine, models.Listing.machine_id == models.Machine.id)
        .filter(models.Machine.provider_id == provider_id)
        .all()
    )


def get_booking_by_id(db: Session, booking_id: int) -> models.Booking | None:
    """Fetches a booking by its primary key."""
    return db.get(models.Booking, booking_id)