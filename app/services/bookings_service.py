from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import models, schemas
from app.repositories import booking_repository, listing_repository


"""
This service defines how bookings behave, including they move from REQUESTED,
to CONFIRMED, become ACTIVE, and then COMPLETE or CANCELLED.

The router calls into this layer whenever the user tries to perform
an action. The repository only reads/writes to the DB. The rules
for what is allowed live here.
"""


def admin_create_booking(db: Session, payload: schemas.BookingCreate):
    """Admin-only primitive for creating bookings directly."""
    return booking_repository.create_booking(db, payload)


def list_bookings_for_user(db: Session, user_id: int):
    """List bookings belonging to a single buyer."""
    return booking_repository.list_bookings_for_user(db, user_id)


def list_all_bookings(db: Session):
    """List ALL bookings. Intended for admin/provider usage."""
    return booking_repository.list_bookings(db)


def request_booking(
    db: Session,
    listing_id: int,
    buyer_user_id: int,
    start_time: datetime,
    end_time: datetime,
):
    """
    This is the flow buyers use when they request a booking.
    We calculate the estimated price up front so the buyer can
    preview what they'll pay, but the final billing happens once the
    active session ends.
    """
    listing = listing_repository.get_listing_by_id(db, listing_id)
    if not listing:
        raise ValueError("Listing not found")

    #Estimated price is based on booked usage window, this dependds on exact second usage
    total_price = ((end_time - start_time).total_seconds() / 3600) * listing.price

    #Create and store the booking object
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


def _get_booking_or_404(db: Session, booking_id: int) -> models.Booking:
    """Get a booking or return an error if not possible"""
    booking = booking_repository.get_booking_by_id(db, booking_id)
    if not booking:
        raise ValueError("Booking not found")
    return booking


def confirm_booking(db: Session, booking_id: int):
    """
    Providers/admins call this when approving a buyer's request.
    A booking can only be confirmed once. After that point,
    session start/end rules apply.
    """
    booking = _get_booking_or_404(db, booking_id)
    booking.status = models.BookingStatus.CONFIRMED
    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(db: Session, booking_id: int):
    """
    Cancel only an existing booking.
    """
    booking = _get_booking_or_404(db, booking_id)
    booking.status = models.BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    return booking


def start_session(db: Session, booking_id: int):
    """
    A session can only begin during the reserved window.
    We disallow starting outside it because usage is tied to billing
    and the hosting provider's capacity planning.
    """
    booking = booking_repository.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    #Can only start from CONFIRMED state
    if booking.status != models.BookingStatus.CONFIRMED:
        raise HTTPException(status_code=409, detail=f"Cannot start; current status is '{booking.status}'")

    #Disallow multiple active sessions
    if booking.active_session_start is not None:
        raise HTTPException(status_code=409, detail="Session already started")

    now = datetime.now(timezone.utc)

    #Validate session timing window
    if now < booking.start_time:
        raise HTTPException(status_code=400, detail="Cannot start before booking start_time")
    if now > booking.end_time:
        raise HTTPException(status_code=400, detail="Cannot start; booking window expired")

    #Mark as active
    booking.active_session_start = now
    booking.status = models.BookingStatus.ACTIVE

    db.commit()
    db.refresh(booking)
    return booking


def end_session(db: Session, booking_id: int):
    """
    Final billing is based on exact session duration, not the planned window.
    We compute the per-second cost using the listing's hourly price and round
    to cents for storage.
    """
    booking = booking_repository.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    #Must be currently active
    if booking.status != models.BookingStatus.ACTIVE:
        raise HTTPException(status_code=409, detail=f"Cannot end; current status is '{booking.status}'")

    #Prevent ending twice
    if booking.active_session_end is not None:
        raise HTTPException(status_code=409, detail="Session already ended")

    now = datetime.now(timezone.utc)
    booking.active_session_end = now

    """
    This should never happen unless the DB is inconsistent.
    We keep this guard to prevent bad billing behavior.
    """
    if not booking.listing:
        raise HTTPException(status_code=500, detail="Listing not attached to booking")

    #Calculate duration and exact charge
    elapsed_seconds = (now - booking.active_session_start).total_seconds()
    booking.usage_seconds = elapsed_seconds
    elapsed_hours = elapsed_seconds / 3600.0
    booking.actual_price_charged = round(float(booking.listing.price) * elapsed_hours, 2)

    booking.status = models.BookingStatus.COMPLETED

    db.commit()
    db.refresh(booking)
    return booking