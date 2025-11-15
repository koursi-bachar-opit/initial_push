from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models, schemas


def get_listings(db: Session):
    """Return all listings sorted by ID (ascending)."""
    return db.query(models.Listing).order_by(models.Listing.id.asc()).all()


def create_listing(db: Session, data: schemas.ListingCreate):
    """Create a new listing record and persist to the database."""
    obj = models.Listing(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_booking(db: Session, data: schemas.BookingCreate):
    """
    Create a booking for a given listing (admin primitive).

    - Validates that the listing exists
    - Checks start < end
    - Estimates total price
    - Requires buyer_user_id to be provided in the payload
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

    # Compute duration (ceil to next hour)
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
    """Return ALL bookings — FOR ADMINS ONLY."""
    return (
        db.query(models.Booking)
        .order_by(models.Booking.id.asc())
        .all()
    )


def list_bookings_for_user(db: Session, user_id: int):
    """Return only the bookings belonging to the authenticated user."""
    return (
        db.query(models.Booking)
        .filter(models.Booking.buyer_user_id == user_id)
        .order_by(models.Booking.id.asc())
        .all()
    )