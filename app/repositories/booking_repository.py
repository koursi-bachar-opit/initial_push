from sqlalchemy.orm import Session

from app import models

def create_booking(db: Session, booking: models.Booking) -> models.Booking: 
    """
    Persist a fully constructed Booking ORM instance.
    All validation and domain rules must be handled by the service layer.
    """
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def update_booking(db: Session, booking: models.Booking) -> models.Booking:
    """
    Return bookings whose states have been changed
    """
    db.commit()
    db.refresh(booking)
    return booking


def list_bookings(db: Session):
    """
    in future: list_all_bookings, list_bookings_for_admin
    Repository returns all records; filtering by user/provider/admin occurs in service.
    """
    return (
        db.query(models.Booking)
        .order_by(models.Booking.id.asc())
        .all()
    )


def list_bookings_for_user(db: Session, user_id: int):
    """
    Return all bookings where buyer_user_id == user_id.
    Caller is responsible for access control
    """
    return (
        db.query(models.Booking)
        .filter(models.Booking.buyer_user_id == user_id)
        .order_by(models.Booking.id.asc())
        .all()
    )


def list_bookings_for_provider(db: Session, provider_id: int):
    """
    Return all bookings associated with machines owned by the given provider_id.
    """
    return (
        db.query(models.Booking)
        .join(models.Booking.listing)
        .join(models.Listing.machine)
        .filter(models.Machine.provider_id == provider_id)
        .order_by(models.Booking.id.asc())  #consider ordering by start_time or created_at
        .all()
    )


def get_booking_by_id(db: Session, booking_id: int) -> models.Booking | None:
    """Fetches a booking by its primary key."""
    return db.get(models.Booking, booking_id)