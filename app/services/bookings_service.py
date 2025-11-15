from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models


# This service layer file handles all business logic related to Bookings.
# Each function corresponds to an action in the booking lifecycle:
# request → confirm → cancel → start → end


def request_booking(
    db: Session,
    listing_id: int,
    buyer_user_id: int,
    start_time: datetime,
    end_time: datetime,
):
    """
    Create a new booking request for a specific listing.

    Steps:
    1. Fetch the listing from the database using its ID.
    2. Validate that the listing exists.
    3. Calculate the estimated total price based on duration (in hours * price).
    4. Create a new Booking record with 'REQUESTED' status and buyer_user_id.
    5. Persist and return the new booking.
    """
    listing = db.get(models.Listing, listing_id)
    if not listing:
        raise ValueError("Listing not found")

    # Calculate total estimated price based on hours of usage
    total_price = ((end_time - start_time).total_seconds() / 3600) * listing.price

    # Create and store the booking object
    booking = models.Booking(
        listing_id=listing_id,
        buyer_user_id=buyer_user_id,
        start_time=start_time,
        end_time=end_time,
        total_price_estimate=total_price,
        status=models.BookingStatus.REQUESTED,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def confirm_booking(db: Session, booking_id: int):
    """
    Update a booking's status from REQUESTED → CONFIRMED.

    - Used by providers to approve customer requests.
    - Raises ValueError if the booking ID doesn't exist.
    """
    booking = db.get(models.Booking, booking_id)
    if not booking:
        raise ValueError("Booking not found")

    booking.status = models.BookingStatus.CONFIRMED
    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(db: Session, booking_id: int):
    """
    Cancel an existing booking.

    - Can be used by either buyer or provider (depending on auth logic).
    - Simply marks the booking as CANCELLED and commits.
    """
    booking = db.get(models.Booking, booking_id)
    if not booking:
        raise ValueError("Booking not found")

    booking.status = models.BookingStatus.CANCELLED
    db.commit()
    return booking


def start_session(db: Session, booking_id: int):
    """
    Begin a server usage session for a confirmed booking.

    Steps:
    1. Validate booking exists and is CONFIRMED.
    2. Prevent re-starting an already active session.
    3. Ensure current time is within [start_time, end_time].
    4. Record the session start timestamp and mark status ACTIVE.
    """
    booking = db.get(models.Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Can only start from CONFIRMED state
    if booking.status != models.BookingStatus.CONFIRMED:
        raise HTTPException(status_code=409, detail=f"Cannot start; current status is '{booking.status}'")

    # Disallow multiple active sessions
    if booking.active_session_start is not None:
        raise HTTPException(status_code=409, detail="Session already started")

    now = datetime.now(timezone.utc)

    # Validate session timing window
    if now < booking.start_time:
        raise HTTPException(status_code=400, detail="Cannot start before booking start_time")
    if now > booking.end_time:
        raise HTTPException(status_code=400, detail="Cannot start; booking window expired")

    # Mark as active
    booking.active_session_start = now
    booking.status = models.BookingStatus.ACTIVE

    db.commit()
    db.refresh(booking)
    return booking


def end_session(db: Session, booking_id: int):
    """
    End an active server session and calculate final billing.

    Steps:
    1. Ensure booking exists and status == ACTIVE.
    2. Record session end time.
    3. Calculate total usage in seconds.
    4. Compute actual price charged (minute precision).
    5. Mark booking as COMPLETED.
    """
    booking = db.get(models.Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Must be currently active
    if booking.status != models.BookingStatus.ACTIVE:
        raise HTTPException(status_code=409, detail=f"Cannot end; current status is '{booking.status}'")

    # Prevent ending twice
    if booking.active_session_end is not None:
        raise HTTPException(status_code=409, detail="Session already ended")

    now = datetime.now(timezone.utc)
    booking.active_session_end = now

    # Verify associated listing for price reference
    if not booking.listing:
        raise HTTPException(status_code=500, detail="Listing not attached to booking")

    # Calculate duration and exact charge
    elapsed_seconds = (now - booking.active_session_start).total_seconds()
    booking.usage_seconds = elapsed_seconds
    elapsed_hours = elapsed_seconds / 3600.0
    booking.actual_price_charged = round(float(booking.listing.price) * elapsed_hours, 2)

    booking.status = models.BookingStatus.COMPLETED

    db.commit()
    db.refresh(booking)
    return booking